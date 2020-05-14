import logging
import networkx as nx
import pandas as pd
import sqlite3

logger = logging.getLogger(__name__)


class QueryCircuit():

    def __init__(self, sqlite_path, sqltable='synlinks',
                 score_thr=60, filter_autapses=True):

        self.cached_links = pd.DataFrame()
        self.cached_seg_ids = set()
        self.score_thr = score_thr
        self.filter_autapses = filter_autapses

        conn = sqlite3.connect(sqlite_path)
        self.cursor = conn.cursor()
        self.sqltable = sqltable

    def get_upstream_partners(self, seg_id, topk=5, weight_threshold=0):

        self.__fetch_links([seg_id])

        nxg = self.links_to_nx(weight_threshold=weight_threshold)
        # networkx predecessors are sorted by weight (decreasing)
        upstream_nodes = list(nxg.predecessors(seg_id))
        return upstream_nodes[:min(len(upstream_nodes), topk)]

    def get_downstream_partners(self, seg_id, topk=5, weight_threshold=0):

        self.__fetch_links([seg_id])

        nxg = self.links_to_nx(weight_threshold=weight_threshold)
        downstream_nodes = list(nxg.successors(seg_id))
        return downstream_nodes[:min(len(downstream_nodes), topk)]

    def get_synaptic_links(self, seg_id, seg_id_partner=None, input_site=True,
                           output_site=True):
        seg_ids = [seg_id]
        if seg_id_partner is not None:
            seg_ids.append(seg_id_partner)
        self.__fetch_links(seg_ids)
        links = self.cached_links.copy()
        if seg_id_partner is None:
            assert input_site or output_site, \
                'Either input_site or output_site needs to be set to True'
            if input_site and output_site:
                links = links[(links.segmentid_pre == seg_id) | (
                        links.segmentid_post == seg_id)]
            if input_site and not output_site:
                links = links[links.segmentid_pre == seg_id]
            if output_site and not input_site:
                links = links[links.segmentid_post == seg_id]
        else:
            downcond = ((links.segmentid_pre == seg_id) & (
                    links.segmentid_post == seg_id_partner))
            upcond = ((links.segmentid_pre == seg_id_partner) & (
                    links.segmentid_post == seg_id))
            links = links[downcond | upcond]
        return links.reset_index(drop=True)

    def links_to_nx(self, seg_ids=None, weight_threshold=0):
        # copy
        if seg_ids is not None:
            self.__fetch_links(seg_ids)
            links = self.cached_links.copy()
            links = links[
                links.segmentid_pre.isin(seg_ids) | links.segmentid_post.isin(
                    seg_ids)]
        else:
            links = self.cached_links.copy()

        links = links[(links.segmentid_pre != 0) & (
                    links.segmentid_post != 0)]
        links = links.reset_index(drop=True)
        # Series assignment only works if index has been reset before!
        links['edges'] = pd.Series(
            list(zip(links.segmentid_pre, links.segmentid_post)))
        c_edges = links.edges.value_counts()
        c_edges = c_edges[c_edges >= weight_threshold]
        nxg = nx.DiGraph()
        for k, v in c_edges.to_dict().items():
            nxg.add_edge(k[0], k[1], weight=v)
        return nxg

    def __fetch_links(self, seg_ids):
        new_seg_ids = set(seg_ids) - self.cached_seg_ids
        if len(new_seg_ids) == 0:
            return

        new_seg_ids_str = [str(seg_id) for seg_id in new_seg_ids]
        cols = ['pre_x', 'pre_y', 'pre_z', 'post_x', 'post_y',
                'post_z', 'scores', 'segmentid_pre', 'segmentid_post',
                'cleft_scores']
        condition = '(segmentid_pre IN ({})) OR (segmentid_post IN ({})'. \
            format(','.join(new_seg_ids_str), ','.join(new_seg_ids_str))
        command = 'SELECT {} from {} WHERE {});'.format(
            ','.join(cols), self.sqltable, condition)
        logger.debug('sql query: %s', command)
        self.cursor.execute(command)
        pre_links = self.cursor.fetchall()
        links = pd.DataFrame.from_records(pre_links, columns=cols)
        if self.filter_autapses:
            links = links[links.segmentid_pre != links.segmentid_post]
        if self.score_thr > 0:
            links = links[links.scores >= self.score_thr]
        links = pd.concat([self.cached_links, links])
        self.cached_links = links.drop_duplicates()
        self.cached_seg_ids.update(new_seg_ids)

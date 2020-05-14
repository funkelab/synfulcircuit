from IPython.core.display import display, HTML
import matplotlib.pyplot as plt
import networkx as nx
import neuroglancer as ng
import json


def plot_circuit(nxg, seg_ids=None,
                 remove_orphan_nodes=True, add_node_ids=False,
                 color_node_ids=None):
    if seg_ids is not None:
        nxg = nxg.subgraph(seg_ids)
        nxg = nx.DiGraph(nxg)  # copy, otherwise graph frozen
    if remove_orphan_nodes:
        nxg.remove_nodes_from(list(nx.isolates(nxg)))
    plt.figure(figsize=(10, 10))
    plt.rcParams.update({'font.size': 22})
    pos = nx.layout.spring_layout(nxg, k=5, weight='weight', seed=1)
    node_sizes = 100
    nx.draw_networkx_nodes(nxg, pos, node_size=node_sizes,
                           node_color='blue',
                           label='neuron segment')
    nx.draw_networkx_edges(nxg, pos, node_size=node_sizes,
                           arrowstyle='->',
                           arrowsize=10, edge_color='black',
                           edge_cmap=plt.cm.Blues, width=2,
                           connectionstyle='arc3,rad=0.1',
                           label='edge weight')
    labels = nx.get_edge_attributes(nxg, 'weight')
    nx.draw_networkx_edge_labels(nxg, pos, edge_labels=labels)

    if color_node_ids is not None:
        nx.draw_networkx_nodes(nxg, pos, nodelist=color_node_ids,
                               node_color='#834D9D')
    if add_node_ids:
        nx.draw_networkx_labels(nxg, pos, font_size=20)

    ax = plt.gca()
    ax.set_axis_off()
    plt.legend()
    plt.show()


def plot_input_output_sites(links, seg_id, input_site_color='#72b9cb',
                            output_site_color='#c12430'):
    pre_links = links[links.segmentid_pre == seg_id]
    post_links = links[links.segmentid_post == seg_id]
    fig = plt.figure(figsize=(10, 10))
    plt.rcParams.update({'font.size': 22})
    ax = fig.add_subplot(111)
    ax.scatter(pre_links.pre_x, pre_links.pre_y, color=output_site_color,
               s=2.5, alpha=1.0, label='output site')
    ax.scatter(post_links.post_x, post_links.post_y, color=input_site_color,
               s=2.5, alpha=1.0, label='input site')
    plt.xticks([])
    plt.yticks([])
    plt.title('Input and output sites of seg id {}'.format(seg_id))
    plt.legend(markerscale=5., scatterpoints=1, fontsize=20)
    plt.show()


def plot_up_downstream_subcircuit(nxg, seg_id, weight_threshold=5,
                                  topk=5, add_node_ids=False):
    #     nxg = self.links_to_nx(weight_threshold=weight_threshold)
    plt.figure(figsize=(10, 10))
    plt.rcParams.update({'font.size': 22})
    downstream_nodes = list(nxg.predecessors(seg_id))
    downstream_nodes = downstream_nodes[:min(len(downstream_nodes), topk)]
    upstream_nodes = list(nxg.neighbors(seg_id))
    upstream_nodes = upstream_nodes[:min(len(upstream_nodes), topk)]
    all_nodes = [seg_id] + downstream_nodes + upstream_nodes

    sub_g = nxg.subgraph(all_nodes)

    pos = nx.spring_layout(sub_g, k=5, weight='weight')
    nx.draw_networkx_nodes(sub_g, pos, nodelist=downstream_nodes,
                           node_color='#F2A431', label='downstream seg ids',
                           alpha=0.5)
    nx.draw_networkx_nodes(sub_g, pos, nodelist=upstream_nodes,
                           node_color="#55B849", label='upstream seg ids',
                           alpha=0.5)
    nx.draw_networkx_nodes(sub_g, pos, nodelist=[seg_id],
                           node_color='#834D9D')
    nx.draw_networkx_edges(sub_g, pos, arrowstyle='->',
                           arrowsize=10, edge_color='black',
                           edge_cmap=plt.cm.Blues, width=2,
                           connectionstyle='arc3,rad=0.1',
                           label='edge weight')

    labels = nx.get_edge_attributes(sub_g, 'weight')
    nx.draw_networkx_edge_labels(sub_g, pos, edge_labels=labels)
    plt.title(
        'Upstream and downstram neuron partner of segmentation id {}'.format(
            seg_id))
    if add_node_ids:
        nx.draw_networkx_labels(sub_g, pos, font_size=20)
    plt.legend(bbox_to_anchor=(0.01, 0.01))
    plt.show()


def ng_link(seg_ids, viewer_state_json, seg_layer):
    with open(viewer_state_json, 'r') as f:
        dic = json.load(f)
    state = ng.viewer_state.ViewerState(dic)
    state.layers[seg_layer].segments = seg_ids
    url = ng.url_state.to_url(state)
    seg_ids = ','.join([str(seg_id) for seg_id in seg_ids])
    text = 'Neuroglancer link with seg ids'
    display(HTML("""<a href="{}">{} {}</a>""".format(url, text, seg_ids)))

# SynfulCircuit: A small library for querying neural circuits

This python-based library allows to query and further analyze neural circuits based on predicted synaptic partners and segmented neurons in volumetric Electron-Microscopy datasets of brain tissue.


## System Requirements
- Hardware requirements
  - No special hardware requirements - standard computer with enough RAM (~ 8 GB, of course: more is always better).
- Software requirements
  -  Software has been tested on Linux (Ubuntu 16.04)

## Installation Guide
from source (creating a conda env is optional, but recommended). Installation takes ~ 3 minutes.
- Clone this repository.
- In a terminal:

```bash
conda create -n <conda_env_name> python=3.6
source activate <conda_env_name>
cd synfulcircuit
pip install -r requirements.txt
python setup.py install
```

See [this jupyter notebook](examples/synful_fafb_query_circuit.ipynb) as an example of how to use this repository to interact with predicted synapses in the FAFB dataset (also see next [section](Example:-Synaptic-Partners-in-a-Whole-Brain-Drosophila-EM-dataset-(FAFB))).

## Example: Synaptic Partners in a Whole-Brain Drosophila EM dataset (FAFB)
In the FAFB dataset \[Zheng et al. 2018\], 244M predicted synaptic partners \[Buhmann et al. 2019\] have been intersected with an automatically generated neuron segmentation \[Li et al. 2019\].
This library allows to query the combined dataset.

For instance, for a given neuron segment id, all up-and downstream neurons can be retrieved. In this example, the downstream neuron partners of the pink neuron projecting from the lobula (brain area marked in blue, part of the visual pathway) are displayed (using neuroglancer).

![ng_visual_pathway](docs/_static/ng_visual_pathway.png)

You can download the combined dataset (244M predicted synapses mapped onto neuron segments) [here](https://cremi.org/static/data/20191211_fafbv14_buhmann2019_li20190805.db). This sql dump has a size of 15 GB.


See [this jupyter notebook](examples/synful_fafb_query_circuit.ipynb) for more details. You need to add the path of the downloaded file in the first jupyter cell:
```python
synaptic_predictions_dump_fname ='' # Put here the path to the downloaded file
```

The runtime of the entire example notebook is ~2 minutes.

## Background: Circuit Reconstruction
In volumetric EM datasets, neurons need to be identified together with synapses to be able to reconstructed the neural circuit (the Connectome).
In this tiny example, detected synaptic partners intersected with a neuron segmentation is used to retrieve the underlying neural circuit:

![circuit_reconstruction](docs/_static/circuit_reconstruction.png)
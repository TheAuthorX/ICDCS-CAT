### Codes and part of real dataset for the ICDCS submission

Experiments are based on Python 3.8. To install all required libs, run:

```pip install -r requirements.txt```

#### File organization and steps to run experiments

##### Configuration files
- ``cfgs/real.yaml``: the parameters used to preprocess the ETH raw data and conduct experiments by using real datasets.
- ``cfgs/synthetic.yaml``: the parameters to generate synthetic datasets and conduct experiments by using synthetic datasets.
- ``cfgs/simulate.yaml``: the parameters to conduct the simulation experiment of zkSync and zkCAT. System parameters are obtained from real systems.
- ``cfgs/real_figures.yaml``: the parameters to draw experimental figures of real dataset experiments.
- ``cfgs/test.yaml``: the parameters for test experiments.

##### Dataset Generation
- ``dataset/generate_real_data.py``: generate real dataset based on the raw data obtained from the Google BigQuery.
- ``dataset/query.py``: the SQLs used to query raw ETH data from the Google BigQuery API.
- ``dataset/generate_synthetic_data.py``: generate synthetic dataset

The preprocessed real datasets are under the folder of ``dataset/real``

To generate other real datasets:

1. follow the instruction on https://cloud.google.com/bigquery to configure your personal Google Bigquery APIs
2. ```
   cd dataset/
   python query.py 
   ```
3. modify the ``cfgs/real.yaml`` to configure your experiments
4. ```python generate_real_data.py --cfg ../cfgs/real.yaml```

To generate synthetic datasets:

1. modify the ``cfgs/synthetic.yaml`` to configure your experiments
2. ```
   cd dataset/
   python generate_synthetic_data.py --cfg ../cfgs/sythetic.yaml
   ```
   
To generate synthetic datasets for simulation experiments (varying the Zipfian coefficient):

1. modify the ``cfgs/simulate.yaml`` and set the exp_type as synthetic in the cfg file.
2. ```
   cd dataset/
   python generate_synthetic_data.py --cfg ../cfgs/simulate.yaml
   ```
   
##### Optimization Algorithms:

- ``experiments/bf_search.py``: the naive Brute-force search algorithm to find the optimal solution.
- ``experiments/best_effort.py``: the best effort algorithm to pack as many transactions as possible to maximize the profit of miners.
- ``experiments/dp.py``: the dynamic programing-based algorithm to find the optimal solution.
- ``experiments/min_density.py``: the minD algorithm to get the approximation solution.

To conduct experiment on each algorithm:

1. modify the ``cfgs/real.yaml`` or ``cfgs/synthetic.yaml`` based on the dataset.
2. ```python the_algorithm.py --cfgs 'path_to_the_cfg'```

##### System Simulation:

To conduct experiment to simulate the performance of systems.

1. modify the ``cfgs/simulate.yaml`` to set parameters related to systems
2. ```cd experiments/```
3. ```python simulation.py --cfgs cfgs/simulate.yaml``` to obtain the result of throughput latency and storage cost.
4. ```python abort_rate.py --cfgs cfgs/simulate.yaml``` to obtain the result of abort rate



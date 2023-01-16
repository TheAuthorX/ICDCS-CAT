# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the synthetic data generation

import numpy as np
import scipy.stats as stats
import argparse
import yaml
from pathlib import Path
from utils import save_data, parse_path

def generate(subsets, tx_count, set_distribution, size_distribution, seed):
    np.random.seed(seed)
    txs = []        # list of transactions tuples: (id, [covered subsets], size)
    covered_subset_count = np.ones(tx_count)    # the covered subset count of each transaction
    tx_size = np.ones(tx_count)         # the size of each transaction

    set_dist, set_mu, set_std = set_distribution[0], float(set_distribution[1][0]), float(set_distribution[1][1])
    size_dist, size_mu, size_std = size_distribution[0], float(size_distribution[1][0]), float(size_distribution[1][1])

    if set_dist == 'normal':
        covered_subset_count = np.random.normal(set_mu, set_std, tx_count)
        covered_subset_count[covered_subset_count < 1] = 1  # we do not consider a TX involving no subset
        covered_subset_count[covered_subset_count > subsets] = subsets  # the covered subsets cannot exceed the number of all subsets
        covered_subset_count = [int(round(numb)) for numb in covered_subset_count]
    elif set_dist == 'uniform':
        # for uniform distribution, (a+b)/2 = mu, (b-a)^2/12 = std^2
        set_low, set_high = set_mu - np.sqrt(3) * set_std , set_mu + np.sqrt(3) * set_std
        covered_subset_count = np.random.randint(set_low, set_high, tx_count)
    elif set_dist == 'power_law':
        # here we only use the first parameter as the a of the power law distribution
        a = set_mu
        covered_subset_count = subsets * np.random.power(a, tx_count)
        covered_subset_count = [int(round(numb)) for numb in covered_subset_count]
    else:
        raise NotImplementedError

    if size_dist == 'normal':
        tx_size = np.random.normal(size_mu, size_std, tx_count)
    elif size_dist == 'uniform':
        size_low, size_high = size_mu - np.sqrt(3) * size_std , size_mu + np.sqrt(3) * size_std
        tx_size = np.random.uniform(size_low, size_high, tx_count)
    elif size_dist == 'power_law':
        a = size_mu
        tx_size = subsets * np.random.power(a, tx_count)
    else:
        raise NotImplementedError

    tx_size[tx_size < 1] = 1  # we assume the minimum unit of size is 1
    tx_size = [int(round(numb)) for numb in tx_size]

    # the item format is (id, [covered subsets], size)
    for index in range(tx_count):
        temp = np.random.choice(subsets, covered_subset_count[index], replace=False).tolist()
        temp = ','.join([str(i) for i in temp])
        txs.append(str(index) + ';' + temp + ';' + str(tx_size[index]) + '\n')

    save_data(txs, parse_path(tx_count, subsets, seed, set_distribution, size_distribution))


def zipfian(a, N):
    x = np.arange(1, N + 1)
    weights = x ** (-a)
    weights = weights.astype(np.float)
    weights /= weights.sum()
    bounded_zipf = stats.rv_discrete(name='bounded_zipf', values=(x, weights))
    return bounded_zipf


def generate_for_simulation(a, subsets, tx_count, size_distribution, seed):
    np.random.seed(seed)
    txs = []  # list of transactions tuples: (id, [covered subsets], size)
    tx_size = np.ones(tx_count)  # the size of each transaction

    size_dist, size_mu, size_std = size_distribution[0], float(size_distribution[1][0]), float(size_distribution[1][1])

    if size_dist == 'normal':
        tx_size = np.random.normal(size_mu, size_std, tx_count)
    elif size_dist == 'uniform':
        size_low, size_high = size_mu - np.sqrt(3) * size_std , size_mu + np.sqrt(3) * size_std
        tx_size = np.random.uniform(size_low, size_high, tx_count)
    elif size_dist == 'power_law':
        a = size_mu
        tx_size = subsets * np.random.power(a, tx_count)
    else:
        raise NotImplementedError

    tx_size[tx_size < 1] = 1  # we assume the minimum unit of size is 1
    tx_size = [int(round(numb)) for numb in tx_size]

    zipf = zipfian(a, subsets)

    # the item format is (id, [covered subsets], size)
    for index in range(tx_count):
        print("generating the {}-th transaction.".format(index))
        print("the minimum prob is : {}".format(zipf.pmf(subsets)))
        covers = []
        while len(covers) == 0:
            for i in range(1, subsets + 1):
                if np.random.random() < zipf.pmf(i):
                    covers.append(i - 1)
        covers = ','.join([str(i) for i in covers])
        txs.append(str(index) + ';' + covers + ';' + str(tx_size[index]) + '\n')

    save_data(txs, parse_path(tx_count, subsets, seed, size_distribution = size_distribution, zipfian=a))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default='../cfgs/synthetic.yaml',
                        help='the configuration yaml file')
    parser.add_argument('--txn', type=int, default=100,
                        help='number of candidate transactions')
    parser.add_argument('--subsets', type=int, default=16,
                        help='number of system state subsets')
    parser.add_argument('--set-dist', type=str, default="normal",
                        help='the distribution of the number of covered subsets (e.g., normal, uniform, power-law)')
    parser.add_argument('--size-dist', type=str, default="normal",
                        help='the distribution of the size of transactions (e.g., normal, uniform, power-law)')
    parser.add_argument('--seed', type=int, default=2602,
                        help='set random seed')
    parser.add_argument('--set-parameters', type=str, default="2,1",
                        help='parameters of the distribution of the number of covered subsets (e.g., mu, sigma for normal distribution)')
    parser.add_argument('--size-parameters', type=str, default="10,1",
                        help='parameters of the distribution of the size of transactions (e.g., mu, sigma for normal distribution)')
    opt = parser.parse_args()

    if opt.cfg and Path(opt.cfg).exists():
        if not 'simulate' in opt.cfg:
            with open(Path(opt.cfg)) as f:
                cfg = yaml.safe_load(f)
            seed_list = cfg['seed_list']
            txn_list, default_txn = cfg['txn_list'], cfg['default_txn']
            subsets_list, default_subset = cfg['subsets_list'], cfg['default_subset']
            default_set_dist, default_size_dist = cfg['default_set_dist'], cfg['default_size_dist']
            set_dist_list, size_dist_list = cfg['set_dist_list'], cfg['size_dist_list']
            set_dist_mu_list = cfg['set_dist_mu_list']
            dist_std_proportion_list = cfg['dist_std_proportion_list']

            for seed in seed_list:
                print(seed)
                # vary number of candidate transactions
                for txn in txn_list:
                    generate(subsets=default_subset, tx_count=txn,
                             set_distribution=default_set_dist,
                             size_distribution=default_size_dist,
                             seed=seed)
                # vary number of covered subsets
                for subsets in subsets_list:
                    generate(subsets=subsets, tx_count=default_txn,
                             set_distribution=default_set_dist,
                             size_distribution=default_size_dist,
                             seed=seed)
                # vary set distribution (mu and std)
                for set_dist in set_dist_list:
                    for mu in set_dist_mu_list:
                        generate(subsets=default_subset, tx_count=default_txn,
                                    set_distribution=[set_dist, [str(mu), str(round(mu * 0.2, 1))]],
                                    size_distribution=default_size_dist,
                                    seed=seed)
                for set_dist in set_dist_list:
                    for std_p in dist_std_proportion_list:
                        generate(subsets=default_subset, tx_count=default_txn,
                                 set_distribution=[set_dist, ['4', str(round(4 * std_p, 1))]],
                                 size_distribution=default_size_dist,
                                 seed=seed)
                # vary size distribution (std only)
                for size_dist in size_dist_list:
                    for std_p in dist_std_proportion_list:
                        generate(subsets=default_subset, tx_count=default_txn,
                                 set_distribution=default_set_dist,
                                 size_distribution=[size_dist, ['100', str(int(100 * std_p))]],
                                 seed=seed)
        else:
            # generate the data for system simulation with different transaction correlation
            with open(Path(opt.cfg)) as f:
                cfg = yaml.safe_load(f)

            subsets_list = cfg['subsets_list']
            zipfian_list = cfg['zipfian_list']
            tx_count = cfg['tx_count']
            size_dist = cfg['size_dist']
            seed_list = cfg['seed_list']

            for subsets in subsets_list:
                for a in zipfian_list:
                    for seed in seed_list:
                        print('generating the file a={}, subsets={}, seed={}'.format(a, subsets, seed))
                        generate_for_simulation(a, subsets, tx_count, size_dist, seed)

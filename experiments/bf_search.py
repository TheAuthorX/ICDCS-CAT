# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the brute-force search algorithm to find the optimal solution

from utils import read_data, parse_path
import time
from itertools import combinations
import argparse
import yaml
from pathlib import Path


def bf_search(transactions, subsets, counter1, counter2, capacity):
    opt_txs = None
    max_objective = subsets * capacity
    min_objective = max_objective
    length = len(transactions)

    for i in range(counter2, counter1 + 1):
        for txs in combinations(transactions, i):
            print('trying comb({}, {})'.format(length, i))
            covers, size = set(), 0
            for t in txs:
                covers |= set(t[1])
                size += t[2]
            objective = max_objective - subsets * size + len(covers)
            if objective < min_objective:
                min_objective = objective
                opt_txs = txs

    return min_objective, opt_txs


def run_exp(capacity, tx_count, subsets, seed, set_distribution, size_distribution, name):
    print("processing seed: {}, subsets: {}, tx_count: {}, capacity: {}".format(seed, subsets, tx_count, capacity))

    transactions = read_data(
        parse_path(tx_count, subsets, seed, set_distribution, size_distribution))

    # compute the maximum number of tx to pick to reduce the search space
    sizes, sum_size, counter1, counter2 = [], 0, 0, 0
    for tx in transactions:
        sizes.append(tx[2])
    sizes.sort()
    for s in sizes:
        sum_size += s
        if sum_size <= capacity:
            counter1 += 1
    sum_size = 0
    for s in reversed(sizes):
        sum_size += s
        if sum_size <= capacity:
            counter2 += 1

    start = time.time()
    (opt_txs, objective) = bf_search(transactions, subsets, counter1, counter2, capacity)
    end = time.time()
    running_time = end - start

    root_path = Path("../outputs/BF_search/{}".format(name))
    root_path.mkdir(parents=True, exist_ok=True)
    result_path = root_path / "{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_{}.txt".format(
        tx_count, subsets, set_distribution, size_distribution, seed)
    f = open(result_path, "w")
    print('The selections is:', file=f)
    print(opt_txs, file=f)
    print('The objective value is:', file=f)
    print(objective, file=f)
    print('time cost : %.5f sec' % running_time, file=f)
    f.close()
    print("Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default="../cfgs/synthetic.yaml",
                        help='the configuration yaml file (see example.yaml)')
    parser.add_argument('--name', type=str, default="exp",
                        help='the name of the experiment')
    opt = parser.parse_args()

    if Path(opt.cfg).exists():
        with open(opt.cfg) as f:
            cfg = yaml.safe_load(f)

        seed_list = cfg['seed_list']
        txn_list, default_txn = cfg['txn_list'], cfg['default_txn']
        subsets_list, default_subset = cfg['subsets_list'], cfg['default_subset']
        default_set_dist, default_size_dist = cfg['default_set_dist'], cfg['default_size_dist']
        set_dist_list, size_dist_list = cfg['set_dist_list'], cfg['size_dist_list']
        set_dist_mu_list = cfg['set_dist_mu_list']
        dist_std_proportion_list = cfg['dist_std_proportion_list']
        default_capacity, capacity_list = cfg['default_capacity'], cfg['capacity_list']

        for seed in seed_list:
            # vary number of candidate transactions
            for txn in txn_list:
                name = "vary_txn"
                run_exp(default_capacity, txn, default_subset, seed, default_set_dist, default_size_dist, name)
            # vary number of covered subsets
            for subsets in subsets_list:
                name = "vary_subsets"
                run_exp(default_capacity, default_txn, subsets, seed, default_set_dist, default_size_dist, name)
            # vary capacity
            for capacity in capacity_list:
                name = "vary_capacity"
                run_exp(capacity, default_txn, default_subset, seed, default_set_dist, default_size_dist, name)
            # vary set distribution (mu and std)
            for set_dist in set_dist_list:
                for mu in set_dist_mu_list:
                    name = "vary_set_dist_mu_{}".format(set_dist)
                    set_distribution = [set_dist, [str(mu), str(round(mu * 0.2, 1))]]
                    run_exp(default_capacity, default_txn, default_subset, seed, set_distribution,
                            default_size_dist,
                            name)
            for set_dist in set_dist_list:
                for std_p in dist_std_proportion_list:
                    name = "vary_set_dist_std_{}".format(set_dist)
                    set_distribution = [set_dist, ['4', str(round(4 * std_p, 1))]]
                    run_exp(default_capacity, default_txn, default_subset, seed, set_distribution,
                            default_size_dist,
                            name)
            # vary size distribution (std only)
            for size_dist in size_dist_list:
                for std_p in dist_std_proportion_list:
                    name = "vary_size_dist_std_{}".format(size_dist)
                    size_distribution = [size_dist, ['100', str(int(100 * std_p))]]
                    run_exp(default_capacity, default_txn, default_subset, seed, default_set_dist,
                            size_distribution,
                            name)
    else:
        print("invalid configuration file!")

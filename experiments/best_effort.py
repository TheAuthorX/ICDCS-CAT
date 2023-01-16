# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the best effort algorithm as our baseline

from utils import read_data, parse_path
import time
import numpy as np
import argparse
import yaml
from pathlib import Path


def find_selected_txs(capacity, transactions, temp_table):
    selected = []
    for i in range(len(transactions) - 1, 0, -1):
        if temp_table[(i, capacity)] > temp_table[(i-1, capacity)]:
            selected.append(i)
            capacity -= transactions[i][2]
    return selected


def DP_fill_core(table, ind, tx_size, c):
    if c-tx_size < 0:
        return table[(ind-1, c)]

    if table[(ind-1, c-tx_size)] + tx_size > table[(ind-1, c)]:
        return table[(ind-1, c-tx_size)] + tx_size
    else:
        return table[(ind-1, c)]


def DP_fill(candidates, capacity):
    temp_table = dict()
    for c in range(capacity + 1):
        if c >= candidates[0][2]:
            temp_table[(0, c)] = candidates[0][2]
        else:
            temp_table[(0, c)] = 0

    for ind in range(1, len(candidates)):
        for c in range(capacity + 1):
            temp_table[(ind, c)] = DP_fill_core(temp_table, ind, candidates[ind][2], c)

    selected = find_selected_txs(capacity, candidates, temp_table)

    return selected, temp_table[(len(candidates) - 1, capacity)]


def best_effort(transactions, subsets, capacity):
    selected_txs, covers = [], set()

    selected_txs, filled_size = DP_fill(transactions, capacity)

    for tx in selected_txs:
        covers |= set(transactions[tx][1])

    objective = subsets * (capacity - filled_size) + len(covers)

    return objective, selected_txs


def run_exp(capacity, tx_count, subsets, seed, set_distribution, size_distribution, name, type=0):
    print("processing seed: {}, subsets: {}, tx_count: {}, capacity: {}".format(seed, subsets, tx_count, capacity))

    transactions = read_data(
        parse_path(tx_count, subsets, seed, set_distribution, size_distribution, real_type=type))

    start = time.time()
    (objective, selected_txs) = best_effort(transactions, subsets, capacity)
    end = time.time()
    running_time = end - start

    if set_distribution and size_distribution:
        # result path for synthetic data result
        root_path = Path("../outputs/Best_effort/synthetic_data/{}".format(name))
        root_path.mkdir(parents=True, exist_ok=True)
        result_path = root_path / "{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_{}.txt".format(
            capacity, tx_count, subsets, set_distribution, size_distribution, seed)
    else:
        # result path for real data result
        root_path = Path("../outputs/Best_effort/real_data/{}".format(name))
        root_path.mkdir(parents=True, exist_ok=True)
        result_path = root_path / "{}_capacity_{}_TXs_{}_subsets_txType_{}_seed_{}.txt".format(
            capacity, tx_count, subsets, type, seed)

    f = open(result_path, "w")
    # print('The selections is:', file=f)
    # print(selected_txs, file=f)
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
                if cfg['tx_type']:
                    for type in cfg['tx_type']:
                        run_exp(default_capacity, txn, default_subset, seed, default_set_dist, default_size_dist, name, type= type)
                else:
                    run_exp(default_capacity, txn, default_subset, seed, default_set_dist, default_size_dist, name)

            # vary number of covered subsets
            for subsets in subsets_list:
                name = "vary_subsets"
                if cfg['tx_type']:
                    for type in cfg['tx_type']:
                        run_exp(default_capacity, default_txn, subsets, seed, default_set_dist, default_size_dist, name, type=type)
                else:
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

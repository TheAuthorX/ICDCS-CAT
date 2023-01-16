# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# The implementation of the minimum-density based algorithm

from utils import read_data, parse_path
import time
import argparse
import yaml
from pathlib import Path


def preprocess_txs(txs):
    temp_ind, temp_cov, temp_size = {}, {}, {}
    grouped_txs = []
    for (ind, sets, size) in txs:
        key = ','.join([str(s) for s in sorted(sets)])
        if key in temp_ind:
            temp_ind[key].append(int(ind))
            temp_size[key] += size
        else:
            temp_ind[key] = [int(ind)]
            temp_cov[key] = sets
            temp_size[key] = size

    for key, v in temp_ind.items():
        grouped_txs.append((v, temp_cov[key], temp_size[key]))
    return grouped_txs


def sorted_density(covered, txs):
    dens = []
    for tx in txs:         # tx[0] is the id, tx[1] is the covered subsets and tx[2] is the size
        dens.append(len(set(tx[1])-covered)/tx[2])

    dens = sorted(enumerate(dens), key=lambda x: x[1])
    idx = [i[0] for i in dens]
    sorted_dens = [i[1] for i in dens]
    return (idx, sorted_dens)


def DP_fill_core(table, ind, tx_size, c):
    if c < 1:
        return 0
    if c-tx_size < 0:
        return table[(ind-1, c)]

    if table[(ind-1, c-tx_size)] + tx_size > table[(ind-1, c)]:
        return table[(ind-1, c-tx_size)] + tx_size
    else:
        return table[(ind-1, c)]


def DP_fill(candidates, capacity):
    temp_table = dict()
    sel = []
    for c in range(capacity + 1):
        if c >= candidates[0][2]:
            temp_table[(0, c)] = candidates[0][2]
        else:
            temp_table[(0, c)] = 0

    for ind in range(1, len(candidates)):
        for c in range(capacity + 1):
            temp_table[(ind, c)] = DP_fill_core(temp_table, ind, candidates[ind][2], c)

    # output selections
    c = capacity
    for ind in range(len(candidates) - 1, -1, -1):
        if ind > 0:
            if (temp_table[(ind, c)] > temp_table[(ind-1, c)]):
                sel.append(candidates[ind][0])  # index
                c -= candidates[ind][2]     # capacity
        elif temp_table[(ind, c)] > 0:
            sel.append(candidates[ind][0])  # index

    return sel, temp_table[(len(candidates) - 1, capacity)]


def find_tx_by_index(txs, ind_list):
    find_txs = []
    for tx in txs:
        if tx[0] in ind_list:
            find_txs.append(tx)
    return find_txs


def MinD(subsets, capacity, txs, grouped_txs):
    covered = set()
    selected = []
    minimum_cap, temp_cover = 99999999, set()
    check_all = False
    temp_cap = capacity

    dp_candidates = []

    while capacity > 0 and not check_all and len(grouped_txs) > 0:
        (sorted_id, sorted_dens) = sorted_density(covered, grouped_txs)
        for id in sorted_id:
            gtx = grouped_txs[id]
            if capacity >= gtx[2]:
                for i in gtx[0]:
                    selected.append(i)
                    dp_candidates += find_tx_by_index(txs, [i])
                capacity -= gtx[2]
                covered |= set(gtx[1])
                grouped_txs.remove(gtx)
                break
            else:
                temp_candidate = dp_candidates + find_tx_by_index(txs, gtx[0])
                sel, cap = DP_fill(temp_candidate, temp_cap)
                if (temp_cap - cap) < minimum_cap:
                    minimum_cap = (temp_cap - cap)
                    temp_cover = set(gtx[1])
                    temp_selection = sel
                    if minimum_cap == 0:
                        capacity = minimum_cap
                        break

            if id == sorted_id[-1]:
                check_all = True

    # if no grouped transactions can fill the remaining capacity exactly then we use the result after applying DP
    if capacity >= minimum_cap:
        capacity = minimum_cap
        covered |= temp_cover
        selected = temp_selection
    objective = subsets * capacity + len(covered)
    return (selected, objective)


def run_exp(capacity, tx_count, subsets, seed, set_distribution, size_distribution, name, type=0):
    print(parse_path(tx_count, subsets, seed, set_distribution, size_distribution, real_type=type))
    transactions = read_data(parse_path(tx_count, subsets, seed, set_distribution, size_distribution, real_type=type))

    print("processing seed: {}, subsets: {}, tx_count: {}, capacity: {}".format(seed, subsets, tx_count, capacity))
    grouped_transactions = preprocess_txs(transactions)

    start = time.time()
    (opt_txs, objective) = MinD(subsets, capacity, transactions, grouped_transactions)
    end = time.time()
    running_time = end - start

    if set_distribution and size_distribution:
        # result path for synthetic data result
        root_path = Path("../outputs/MinD/synthetic_data/{}".format(name))
        root_path.mkdir(parents=True, exist_ok=True)
        result_path = root_path / "{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_{}.txt".format(
            capacity, tx_count, subsets, set_distribution, size_distribution, seed)
    else:
        # result path for real data result
        root_path = Path("../outputs/MinD/real_data/{}".format(name))
        root_path.mkdir(parents=True, exist_ok=True)
        result_path = root_path / "{}_capacity_{}_TXs_{}_subsets_txType_{}_seed_{}.txt".format(
            capacity, tx_count, subsets, type, seed)

    f = open(result_path, "w")
    # print('The selections is:', file=f)
    # print(opt_txs, file=f)
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
                        run_exp(default_capacity, txn, default_subset, seed, default_set_dist, default_size_dist, name, type=type)
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
                    run_exp(default_capacity, default_txn, default_subset, seed, set_distribution, default_size_dist,
                            name)
            for set_dist in set_dist_list:
                for std_p in dist_std_proportion_list:
                    name = "vary_set_dist_std_{}".format(set_dist)
                    set_distribution = [set_dist, ['4', str(round(4 * std_p, 1))]]
                    run_exp(default_capacity, default_txn, default_subset, seed, set_distribution, default_size_dist,
                            name)
            # vary size distribution (std only)
            for size_dist in size_dist_list:
                for std_p in dist_std_proportion_list:
                    name = "vary_size_dist_std_{}".format(size_dist)
                    size_distribution = [size_dist, ['100', str(int(100 * std_p))]]
                    run_exp(default_capacity, default_txn, default_subset, seed, default_set_dist, size_distribution,
                            name)
    else:
        print("invalid configuration file!")

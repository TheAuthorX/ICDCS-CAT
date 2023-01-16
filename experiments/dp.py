# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the DP-based algorithm

from utils import read_data, parse_path
import time
import argparse
import yaml
from pathlib import Path


# convert the h_plus string to a set
def table_entry_to_set(entry):
    if entry == '()':
        return set()
    else:
        return set(map(int, entry[1:-1].split(',')))


def set_to_table_entry(the_set):
    the_list = list(the_set)
    the_list.sort()
    the_set = ','.join(map(str, the_list))
    return '(' + the_set + ')'


def adj_graph(j, subsets):
    global transactions
    indices = []
    sets = set()

    for tx in transactions:
        for k in range(j + 1):
            for l in range(j + 1, subsets):
                if k in tx[1] and l in tx[1]:
                    sets.add(l)

    sets = list(sets)
    return (indices, sets)


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
    print('entering DP fill with capacity {} and {} candidates'.format(capacity, len(candidates)))
    for c in range(capacity + 1):
        if c >= candidates[0][2]:
            temp_table[(0, c)] = candidates[0][2]
        else:
            temp_table[(0, c)] = 0

    for ind in range(1, len(candidates)):
        for c in range(capacity + 1):
            temp_table[(ind, c)] = DP_fill_core(temp_table, ind, candidates[ind][2], c)
    return temp_table[(len(candidates) - 1, capacity)]


def compute_c_v(j, h_plus, capacity, subsets):
    global transactions

    candidates = []
    h_plus.add(j)
    for tx in transactions:
        if j in tx[1] and set(tx[1]).issubset(h_plus):
            candidates.append(tx)

    total_cap = 0
    for tx in candidates:
        total_cap += tx[2]
    if total_cap > capacity:
        c_star = DP_fill(candidates, capacity)
    else:
        c_star = total_cap

    v_star = 1 - subsets * c_star # len(h_plus) - subsets * c_star
    return c_star, v_star


# string to list of powerset
def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]


def compute_h_table(subsets):
    h_table = dict()
    h_table[-1] = [[],[]]
    for j in range(subsets-1):
        h_table[j] = adj_graph(j, subsets)
    h_table[subsets-1] = [[],[]]
    return h_table


def set_of_pick(j, h_plus):
    global h_table
    h_plus.add(j)
    temp = h_plus.intersection(set(h_table[j-1][1]))
    if not temp:
        return ('()', set())
    else:
        return (set_to_table_entry(temp), temp)


def set_of_unpick(j, h_plus):
    global h_table
    temp = h_plus.intersection(set(h_table[j-1][1]))
    if not temp:
        return ('()', set())
    else:
        return (set_to_table_entry(temp), temp)


def DP_core(j, h_plus, capacity, subsets, show = False):
    global table

    # print('computing the entry: ({}, {}, {})'.format(j, h_plus, capacity))

    if (j-1, set_of_unpick(j, h_plus)[0], capacity) not in table:
        table[(j-1, set_of_unpick(j, h_plus)[0], capacity)] = DP_core(j-1, set_of_unpick(j, h_plus)[1], capacity, subsets, show=show)

    temp1 = table[(j-1, set_of_unpick(j, h_plus)[0], capacity)]
    c_star, v_star = compute_c_v(j, h_plus, capacity, subsets)
    if (j-1, set_of_pick(j, h_plus)[0], capacity - c_star) not in table:
        table[(j-1, set_of_pick(j, h_plus)[0], capacity - c_star)] = DP_core(j-1, set_of_pick(j, h_plus)[1], capacity - c_star, subsets, show=show)

    temp2 = table[(j-1, set_of_pick(j, h_plus)[0], capacity - c_star)] + v_star

    if temp1 < temp2:
        return temp1
    else:
        # if show:
        #     pick_list.append(j)
        return temp2


def DP(subsets, capacity):
    global default_value, table

    # initialize the table
    for i in range(capacity + 1):
        # initialize all (0, x) entries
        table[(-1, '()', i)] = default_value

    table[(subsets-1, '()', capacity)] = DP_core(subsets-1, set(), capacity, subsets)

    objective = table[(subsets-1, '()', capacity)]

    # DP_core(subsets - 1, set(), capacity, subsets, show=True)

    return 'not implemented', objective


def run_exp(capacity, tx_count, subsets, seed, set_distribution, size_distribution, name, type=0):
    global h_table, table, transactions, default_value

    print("processing seed: {}, subsets: {}, tx_count: {}, capacity: {}".format(seed, subsets, tx_count, capacity))
    transactions = read_data(
        parse_path(tx_count, subsets, seed, set_distribution, size_distribution, real_type=type))

    start = time.time()
    h_table = compute_h_table(subsets)  # used for state pruning
    table = dict()
    default_value = subsets * capacity
    (opt_txs, objective) = DP(subsets, capacity)
    end = time.time()
    running_time = end - start

    if set_distribution and size_distribution:
        # result path for synthetic data result
        root_path = Path("../outputs/DP/synthetic_data/{}".format(name))
        root_path.mkdir(parents=True, exist_ok=True)
        result_path = root_path / "{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_{}.txt".format(
            capacity, tx_count, subsets, set_distribution, size_distribution, seed)
    else:
        # result path for real data result
        root_path = Path("../outputs/DP/real_data/{}".format(name))
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
        default_capacity, capacity_list =  cfg['default_capacity'],  cfg['capacity_list']

        global h_table, table, transactions, default_value

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
                # it takes too much time to compute the result
                if subsets > 16:
                    continue
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

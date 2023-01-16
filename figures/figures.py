# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the generation of the figures of algorithm related experiments

import argparse
import yaml
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker
from pathlib import Path


def draw_objective_value(filepath, filename, xs, ys, x_title, x_labels=[]):
    plt.clf()

    font = {
        'size': 40
    }
    mpl.rc('font', **font)

    n = len(xs)
    x = np.arange(n) + 1

    DP = ys[0]
    MinD = ys[1]
    BOUND = np.array(ys[0]) * (1 + np.divide(1, np.e))
    BestEffort = ys[2]

    # Set the title and the labels of x-axis and y-axis
    plt.xlabel(x_title, fontsize=40)
    text = plt.ylabel('Objective Value', fontsize=40)

    fig = plt.gcf()
    fig.set_size_inches(10, 7)

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # calculate the interval length
    interval_len = np.ceil(
        np.divide(max(ys[0] + ys[1] + ys[2]), 7))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(interval_len))
    # set the y axis range
    # ax.set_ylim([5, 40])

    plt.bar(x - 0.3, DP, width=0.2, label=r'$DP$', color='#DBD0A7')
    plt.bar(x - 0.1, MinD, width=0.183, label=r'$MinD$', color='#E69B03', edgecolor='#E69B03', lw='2')
    plt.bar(x + 0.1, BOUND, width=0.183, label=r'$BD$', color='#D1494E', edgecolor='#D1494E', lw='2')
    plt.bar(x + 0.3, BestEffort, width=0.2, label=r'$BE$', color='#123555')

    if x_labels:
        group_labels = x_labels
    else:
        group_labels = []
        for temp_x in xs:
            temp_x = np.log2(temp_x)
            group_labels.append(r'$2^{%d}$' % temp_x)

    plt.xticks(x, group_labels, rotation=0)
    leg = ax.legend(prop={'size': 30}, bbox_to_anchor=(1.0, 0.5), loc='center left', borderaxespad=0)

    # plt.show()
    path = Path(filepath)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    plt.savefig('%s.pdf' % (filepath + filename),
                bbox_extra_artists=(leg, text),
                bbox_inches='tight')

def draw_running_time(filepath, filename, xs, ys, x_title, x_labels=[]):
    plt.clf()

    font = {
        'size': 40
    }
    mpl.rc('font', **font)

    n = len(xs)
    x = np.arange(n) + 1

    # x for DP and bound
    try:
        index = ys[0].index(0)
        x_dp = np.arange(index) + 1
        DP = ys[0][0:index]

    except:
        index = -1
        x_dp = np.arange(n) + 1
        DP = ys[0]

    MinD = ys[1]
    BestEffort = ys[2]

    # Set the title and the labels of x-axis and y-axis
    plt.xlabel(x_title, fontsize=40)
    text = plt.ylabel('Running Time (s)', fontsize=40)

    fig = plt.gcf()
    fig.set_size_inches(10, 7)

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_yscale('log', base=2)

    # calculate the interval length
    # interval_len = np.log2(max(ys[0] + ys[1] + ys[2]))
    ax.yaxis.set_major_locator(ticker.LogLocator(base=2.0, numticks=7))
    # set the y axis range
    # ax.set_ylim([5, 40])

    plt.plot(x_dp, DP, marker='^', linewidth=3, markersize=20,
             markeredgecolor='#D1494E', markerfacecolor='#D1494E', markeredgewidth=3,
             label=r'$DP$', color='#D1494E')
    plt.plot(x, MinD, marker='s', linewidth=3, markersize=20,
             markeredgecolor='#E69B03', markerfacecolor='#E69B03', markeredgewidth=3,
             label=r'$MinD$', color='#E69B03')
    plt.plot(x, BestEffort, marker='d', linewidth=3, markersize=20,
             markeredgecolor='#123555', markerfacecolor='#123555', markeredgewidth=3,
             label=r'$BE$', color='#123555')

    if x_labels:
        group_labels = x_labels
    else:
        group_labels = []
        for temp_x in xs:
            temp_x = np.log2(temp_x)
            group_labels.append(r'$2^{%d}$' % temp_x)

    plt.xticks(x, group_labels, rotation=0)
    leg = ax.legend(prop={'size': 30}, bbox_to_anchor=(1.0, 0.5), loc='center left', borderaxespad=0)

    # plt.show()
    path = Path(filepath)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    plt.savefig('%s.pdf' % (filepath + filename),
                bbox_extra_artists=(leg, text),
                bbox_inches='tight')

def compute_average_values(path_prefix, seed_list):
    y, time = 0, 0
    for seed in seed_list:
        file_path = path_prefix + "{}.txt".format(seed)
        if not Path(file_path).exists():
            return 0, 0
            # print('Insufficient results!')
            # print('{} does not exist!'.format(file_path))
            # raise FileNotFoundError
        with open(file_path, 'r') as f:
            lines = f.readlines()
            y += float(lines[1])
            time += float(lines[2].split(' ')[3])
        f.close()

    return y / len(seed_list), time / len(seed_list)


def compute_ratio(result_array):
    # the results are DP, MinD, BE
    (DP, MinD, BE) = result_array
    ratio1 = np.divide(np.subtract(np.array(BE), np.array(DP)), np.array(BE))
    ratio2 = np.divide(np.subtract(np.array(BE), np.array(MinD)), np.array(BE))
    return ratio1, ratio2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default="cfgs/synthetic.yaml",
                        help='the configuration yaml file (see example.yaml)')
    parser.add_argument('--name', type=str, default="exp",
                        help='the name of the experiment')
    opt = parser.parse_args()

    # root_path_list = ['../outputs/DP/synthetic/', '../outputs/MinD/synthetic/', '../outputs/Best_effort/synthetic/']
    root_path_list = ['../outputs/DP/real_data/', '../outputs/MinD/real_data/', '../outputs/Best_effort/real_data/']

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

        # vary number of candidate transactions
        obj_values, running_time = [], []
        name = "vary_txn"
        for root_path in root_path_list:
            temp_y, temp_time = [], []
            for txn in txn_list:
                if cfg['tx_type']:
                    path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_txType_{}_seed_".format(
                                default_capacity, txn, default_subset, cfg['tx_type'][0])
                    filepath = 'figures/real_type{}/'.format(cfg['tx_type'][0])
                else:
                    path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_".format(
                                default_capacity, txn, default_subset, default_set_dist, default_size_dist)
                    filepath = 'synthetic/'
                y, time = compute_average_values(path_prefix, seed_list)
                temp_y.append(y)
                temp_time.append(time)
            obj_values.append(temp_y)
            running_time.append(temp_time)

        print(name)
        print(compute_ratio(obj_values))
        # if len(obj_values[0]) and len(running_time[0]):
        #     draw_objective_value(filepath, name, txn_list, obj_values, '|T|')
        #     draw_running_time(filepath, name + '_time', txn_list, running_time, '|T|')

        # vary number of covered subsets
        obj_values, running_time = [], []
        name = "vary_subsets"
        for root_path in root_path_list:
            temp_y, temp_time = [], []
            for subsets in subsets_list:
                if cfg['tx_type']:
                    path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_txType_{}_seed_".format(
                                default_capacity, default_txn, subsets, cfg['tx_type'][0])
                    filepath = 'figures/real_type{}/'.format(cfg['tx_type'][0])
                else:
                    path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_".format(
                                default_capacity, default_txn, subsets, default_set_dist, default_size_dist)
                    filepath = 'synthetic/'
                y, time = compute_average_values(path_prefix, seed_list)
                temp_y.append(y)
                temp_time.append(time)
            obj_values.append(temp_y)
            running_time.append(temp_time)

        print(name)
        print(compute_ratio(obj_values))
        # if len(obj_values[0]) and len(running_time[0]):
        #     draw_objective_value(filepath, name, subsets_list, obj_values, 'm')
        #     draw_running_time(filepath, name + '_time', subsets_list, running_time, 'm')

        # vary capacity
        obj_values, running_time = [], []
        name = "vary_capacity"
        filepath = 'synthetic/'
        for root_path in root_path_list:
            temp_y, temp_time = [], []
            for capacity in capacity_list:
                path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_".format(capacity, default_txn,
                                                                                                            default_subset,
                                                                                                            default_set_dist,
                                                                                                            default_size_dist)
                y, time = compute_average_values(path_prefix, seed_list)
                temp_y.append(y)
                temp_time.append(time)
            obj_values.append(temp_y)
            running_time.append(temp_time)

        print(name)
        print(compute_ratio(obj_values))
        # if len(obj_values[0]) and len(running_time[0]):
        #     draw_objective_value(filepath, name, np.divide(capacity_list, 100), obj_values, r'$\epsilon$')
        #     draw_running_time(filepath, name + '_time', np.divide(capacity_list, 100), running_time, r'$\epsilon$')


        # vary set distribution (mu and std)
        for set_dist in set_dist_list:
            obj_values, running_time = [], []
            name = "vary_set_dist_mu_{}".format(set_dist)
            for root_path in root_path_list:
                temp_y, temp_time = [], []
                for mu in set_dist_mu_list:
                    set_distribution = [set_dist, [str(mu), str(round(mu * 0.2, 1))]]
                    path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_".format(
                        default_capacity, default_txn, default_subset, set_distribution, default_size_dist)
                    y, time = compute_average_values(path_prefix, seed_list)
                    temp_y.append(y)
                    temp_time.append(time)
                obj_values.append(temp_y)
                running_time.append(temp_time)

            print(name)
            print(compute_ratio(obj_values))
            # if len(obj_values[0]) and len(running_time[0]):
            #   draw_objective_value(filepath, name, set_dist_mu_list, obj_values, r'$\mu$', [str(i) for i in set_dist_mu_list])
            #    draw_running_time(filepath, name + '_time', set_dist_mu_list, running_time, r'$\mu$', [str(i) for i in set_dist_mu_list])
        for set_dist in set_dist_list:
            obj_values, running_time = [], []
            name = "vary_set_dist_std_{}".format(set_dist)
            for root_path in root_path_list:
                temp_y, temp_time = [], []
                for std_p in dist_std_proportion_list:
                    set_distribution = [set_dist, ['4', str(round(4 * std_p, 1))]]
                    path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_".format(
                        default_capacity, default_txn, default_subset, set_distribution, default_size_dist)
                    y, time = compute_average_values(path_prefix, seed_list)
                    temp_y.append(y)
                    temp_time.append(time)
                obj_values.append(temp_y)
                running_time.append(temp_time)

            print(name)
            print(compute_ratio(obj_values))
            # if len(obj_values[0]) and len(running_time[0]):
            #     draw_objective_value(filepath, name, dist_std_proportion_list, obj_values, r'$\sigma$', [str(i * 4) for i in dist_std_proportion_list])
            #     draw_running_time(filepath, name + '_time', dist_std_proportion_list, running_time, r'$\sigma$', [str(i * 4) for i in dist_std_proportion_list])

        # vary size distribution (std only)
        for size_dist in size_dist_list:
            obj_values, running_time = [], []
            name = "vary_size_dist_std_{}".format(size_dist)
            for root_path in root_path_list:
                temp_y, temp_time = [], []
                for std_p in dist_std_proportion_list:
                    size_distribution = [size_dist, ['100', str(int(100 * std_p))]]
                    path_prefix = root_path + name + "/{}_capacity_{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_".format(
                        default_capacity, default_txn, default_subset, default_set_dist, size_distribution)
                    y, time = compute_average_values(path_prefix, seed_list)
                    temp_y.append(y)
                    temp_time.append(time)
                obj_values.append(temp_y)
                running_time.append(temp_time)

            # if len(obj_values[0]) and len(running_time[0]):
            #     draw_objective_value(filepath, name, dist_std_proportion_list, obj_values, r'$\sigma$', [str(i * 4) for i in dist_std_proportion_list])
            #     draw_running_time(filepath, name + '_time', dist_std_proportion_list, running_time, r'$\sigma$', [str(i * 4) for i in dist_std_proportion_list])
    else:
        print("invalid configuration file!")
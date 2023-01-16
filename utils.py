# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements utility functions

from pathlib import Path


def save_data(txs, path):
    print(path.absolute())
    if path.exists():
        print('The file exists!')
    else:
        with open(path, "w", newline='\n') as file:
            file.writelines(txs)
        print("Done!")
    return


def read_data(path):
    txs = []
    with open(path) as file:
        lines = file.readlines()
        for line in lines:
            temp = line.split(';')
            id = int(temp[0])
            covers = [int(i) for i in temp[1].split(',')]
            if 'real' in str(path):
                size = int(int(temp[2]) / 1000)
            else:
                size = int(temp[2])
            txs.append((id, covers, size))
        print('finish reading the file!')
    return txs


def parse_path(tx_count, subsets, seed, set_distribution = None, size_distribution = None, real_type=0, zipfian = -1):
    if set_distribution and size_distribution:
        root_path = Path('../dataset/synthetic').resolve()
        if len(set_distribution) != 2 or len(size_distribution) != 2:
            print('The format of distribution is invalid!')
            print('It should be [the name of the distribution, [parameter 1, parameter 2]]. E.g., [normal, [mu, sigma]]')

        path = root_path / "{}_TXs_{}_subsets_set_dist_{}_size_dist_{}_seed_{}.csv".format(tx_count, subsets, set_distribution, size_distribution, seed)
        return path
    elif zipfian >= 0:
        root_path = Path('../dataset/simulate').resolve()
        path = root_path / "{}_TXs_{}_subset_{}_size_dist_{}_zipfian_seed_{}.csv".format(tx_count, subsets, size_distribution, zipfian, seed)
        return path
    else:
        root_path = Path('../dataset/real').resolve()
        # real_type: 0 means all txs, 1 means contract txs only
        path = root_path / "{}_TXs_{}_subset_type_{}__seed_{}.csv".format(tx_count, subsets, real_type, seed)
        return path


if __name__ == '__main__':
    print("utils.py")

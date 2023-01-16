# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the real dataset generation

import numpy as np
import csv
import argparse
import yaml
from pathlib import Path
from utils import save_data, parse_path


# split the raw data into files based on the block number of each transaction
def preprocess_raw_data(root_path, number_of_files):
    # the data we used is from block number 11,000,000 to 12,000,000
    # from Oct-06-2020 to Mar-08-2021
    # containing in 167 separated files
    if not (root_path / "processed").exists():
        (root_path / "processed").mkdir(parents=True, exist_ok=True)
    else:
        print("Using existing processed files!")
        return

    tx_counter = 0
    for i in range(167):
        path = root_path / "eth{:012d}".format(i)
        print("processing file {}".format(i))
        with open(path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            is_header = True
            for row in spamreader:
                if is_header:
                    is_header = False
                    continue
                block_number = int(row[5])
                if block_number >= 11000000 and block_number < 12000000:
                    tx_counter += 1
                    slot = (block_number - 11000000) / 1000000 * number_of_files
                    start_block = 11000000 + int(slot) * 1000000 / number_of_files
                    end_block = start_block + 1000000 / number_of_files - 1
                    dest_file_name = "block_{}_to_{}.csv".format(int(start_block), int(end_block))
                    dest_file_path = root_path / "processed/{}".format(dest_file_name)
                    with open(dest_file_path, "a", newline='') as dest_file:
                        writter = csv.writer(dest_file, delimiter=',')
                        writter.writerow(row)
    print("Finish splitting {} transactions!".format(tx_counter))
    return


# split the world state into subsets uniformly according to the address
# can only support the number of subsets to be 2^n
def uniform_subset_split(subsets, address):
    ind = int(np.ceil(np.log(subsets)/np.log(16)))
    addr = address[2:(ind+2)]
    slot_length = np.power(16, ind) / subsets
    slot = int(int(addr, 16) / slot_length)
    return slot


# generate the real dataset based on the yaml file
def generate(raw_data_path, subsets, tx_count, seed):
    np.random.seed(seed)
    starting_ind = np.random.randint(11000000, 11900000) # in case there is not enough transactions (use 11900000)
    # generate dataset containing all kinds of transactions and contract transactions only
    all_txs, contract_txs = [], []
    all_txs_counter, contract_txs_counter = 0, 0
    b = int(starting_ind / 20000) * 20000
    file_path = Path(raw_data_path) / 'processed' / 'block_{}_to_{}.csv'.format(b, b + 19999)

    cover_map = dict()  # t_hash : [covered subsets, size]
    # generate dataset containing all kinds of transactions
    with open(file_path, 'r') as f:
        lines = csv.reader(f, delimiter = ',')
        for line in lines:
            # line is in the format (tx_hash, from_address, to_address, state_address, gas, block_number)
            if int(line[5]) >= starting_ind:
                if line[3]:
                    # contract transaction
                    t_hash = line[0]
                    if t_hash != cover_map:
                        cover_map[t_hash] = [{uniform_subset_split(subsets, line[1]), uniform_subset_split(subsets, line[3])},
                            int(line[4]), int(line[5]), 'contract']
                    else:
                        cover_map[t_hash][0] |= uniform_subset_split(subsets, line[3])
                else:
                    # token transfer transaction
                    t_hash = line[0]
                    if t_hash != cover_map:
                        cover_map[t_hash] = [{uniform_subset_split(subsets, line[1]), uniform_subset_split(subsets, line[2])},
                            int(line[4]), int(line[5]), 'transfer']

    transactions = []
    for _, v in cover_map.items():
        transactions.append(v)
    transactions = sorted(transactions, key=lambda x:x[2])

    for tx in transactions:
        if all_txs_counter < tx_count:
            temp = ','.join([str(i) for i in list(tx[0])])
            all_txs.append(str(all_txs_counter) + ';' + temp + ';' + str(tx[1]) + '\n')
            all_txs_counter += 1
        if tx[-1] == 'contract':
            if contract_txs_counter < tx_count:
                temp = ','.join([str(i) for i in list(tx[0])])
                contract_txs.append(str(contract_txs_counter) + ';' + temp + ';' + str(tx[1]) + '\n')
                contract_txs_counter += 1

    if len(contract_txs) < tx_count:
        raise EOFError

    save_data(all_txs, parse_path(tx_count, subsets, seed, real_type=0))
    save_data(contract_txs, parse_path(tx_count, subsets, seed, real_type=1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default='../cfgs/real.yaml',
                        help='the configuration yaml file')
    parser.add_argument('--txn', type=int, default=100,
                        help='number of candidate transactions')
    parser.add_argument('--subsets', type=int, default=16,
                        help='number of system state subsets')
    parser.add_argument('--seed', type=int, default=2602,
                        help='set random seed')
    opt = parser.parse_args()

    if opt.cfg and Path(opt.cfg).exists():
        with open(Path(opt.cfg)) as f:
            cfg = yaml.safe_load(f)

        seed_list = cfg['seed_list']
        default_txn, txn_list = cfg['default_txn'], cfg['txn_list']
        default_subset, subsets_list = cfg['default_subset'], cfg['subsets_list']

        raw_data_path = Path(cfg['raw_data_path'])
        preprocess_raw_data(root_path = raw_data_path, number_of_files=50)

        for seed in seed_list:
            # vary number of candidate transactions
            for txn in txn_list:
               generate(raw_data_path, subsets=default_subset, tx_count=txn, seed=seed)
            # vary number of covered subsets
            for subsets in subsets_list:
                print("generating the file with {} subsets, {} txs and seed {}".format(subsets, default_txn, seed))
                generate(raw_data_path, subsets=subsets, tx_count=default_txn, seed=seed)

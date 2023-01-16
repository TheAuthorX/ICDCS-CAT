# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
import argparse
import yaml
from pathlib import Path
from utils import read_data, parse_path
from simulation import split_batches
import random

def cat(rate, batches, tx_count, subsets):
    processing_table = [['']*subsets for _ in range(len(batches))]

    # build the processing table representing the state in the CM forest
    for i in range(len(batches)):
        _, cov = batches[i]
        if random.random() < rate:
            state = 0
        else:
            state = 1
        for j in cov:
            processing_table[i][j] = state

    # traverse the CM forest to decide abortion
    to_be_zero = set()
    for i in range(len(batches)):
        # for all successive modifications following a failure commitment update, it should be aborted
        for j in to_be_zero:
            if processing_table[i][j] == 1:
                processing_table[i][j] = 0

        if 0 in processing_table[i]:    # if a row (batch) contains failure update
            for j in range(subsets):
                if processing_table[i][j] == 1:     # the entire batch should fail
                    processing_table[i][j] = 0
                    to_be_zero.add(j)   # the successive modifications on the commitment i should fail
                elif processing_table[i][j] == 0:
                    to_be_zero.add(j)

    succ_txs, succ_batches = 0, 0
    for i in range(len(batches)):
        if 1 in processing_table[i]:
            succ_batches += 1
            (txs, _) = batches[i]
            succ_txs += len(txs)

    # compute the abort rate in the unit of batch/block
    abort_rate = (len(batches) - succ_batches) / len(batches)

    # compute the abort rate in the unit of each transaction
    # abort_rate = (tx_count - succ_txs) / tx_count
    return abort_rate


def serialized(rate, batches, tx_count):
    succ_txs, succ_batches = 0, 0

    for i in range(len(batches)):
        if random.random() < rate:
            break
        else:
            succ_batches += 1
            # count succeed transactions
            (txs, _) = batches[i]
            succ_txs += len(txs)

    abort_rate = (len(batches) - succ_batches) / len(batches)  # count abort rate in batch count
    # abort_rate = (tx_count - succ_txs) / tx_count     # count abort rate in transaction count
    return abort_rate


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default="../cfgs/simulate.yaml",
                        help='the configuration yaml file (see cfgs/simulate.yaml)')
    parser.add_argument('--name', type=str, default="simulate",
                        help='the name of the experiment')
    opt = parser.parse_args()

    if Path(opt.cfg).exists():
        with open(opt.cfg) as f:
            cfg = yaml.safe_load(f)

        simulation_round = cfg['round']
        tx_count = cfg['tx_count']
        exp_block_count = cfg['exp_block_count']   # 30 by default
        seed_list = cfg['seed_list']
        f_rates = cfg['failure_rates']
        size_dist = cfg['size_dist']
        exp_type = cfg['exp_type']

        if exp_type == 'real_data':
            subsets_list = cfg['subsets_list']
            zipfian_list = [0]
        else:
            subsets_list = [cfg['default_subsets']]
            zipfian_list = cfg['zipfian_list']

        s_abort_rate_table, c_abort_rate_table = dict(), dict()

        for subsets in subsets_list:
            print("processing the case with {} subsets".format(subsets))
            for zipf in zipfian_list:
                for seed in seed_list:
                    if exp_type == 'real_data':
                        transactions = read_data(parse_path(tx_count, subsets, seed))
                    else:
                        transactions = read_data(parse_path(tx_count, subsets, seed, size_distribution = size_dist, zipfian=zipf))

                    batches = split_batches(transactions, subsets, exp_block_count)

                    for rate in f_rates:        # < rate: fail, >= rate: success
                        avg_s_abort_rate, avg_c_abort_rate = 0, 0
                        for _ in range(simulation_round):      # total round number = round * seeds (for each transaction file)
                            avg_s_abort_rate += serialized(rate, batches, tx_count)
                            avg_c_abort_rate += cat(rate, batches, tx_count, subsets)

                        avg_s_abort_rate /= simulation_round
                        avg_c_abort_rate /= simulation_round
                        if rate in s_abort_rate_table:
                            s_abort_rate_table[rate] += avg_s_abort_rate
                        else:
                            s_abort_rate_table[rate] = avg_s_abort_rate
                        if rate in c_abort_rate_table:
                            c_abort_rate_table[rate] += avg_c_abort_rate
                        else:
                            c_abort_rate_table[rate] = avg_c_abort_rate

                if exp_type == 'real_data':
                    root_path = Path("../outputs/abrot_rate/")
                    root_path.mkdir(parents=True, exist_ok=True)
                    s_path = root_path / "serialized_{}_round_{}_TXs_{}_subsets_{}_exp_blocks.txt".format(
                        simulation_round, tx_count, subsets, exp_block_count)
                    c_path = root_path / "cat_{}_round_{}_TXs_{}_subsets_{}_exp_blocks.txt".format(
                        simulation_round, tx_count, subsets, exp_block_count)
                else:
                    root_path = Path("../outputs/abrot_rate_syn/")
                    root_path.mkdir(parents=True, exist_ok=True)
                    s_path = root_path / "serialized_{}_round_{}_TXs_{}_subsets_{}_exp_blocks_{}_zipf.txt".format(
                        simulation_round, tx_count, subsets, exp_block_count, zipf)
                    c_path = root_path / "cat_{}_round_{}_TXs_{}_subsets_{}_exp_blocks_{}_zipf.txt".format(
                        simulation_round, tx_count, subsets, exp_block_count, zipf)

                s_f, c_f = open(s_path, "w"), open(c_path, "w")
                for rate in f_rates:
                    s_abort_rate_table[rate] /= len(seed_list)
                    print("f rate: {}".format(rate), file=s_f)
                    print(s_abort_rate_table[rate], file=s_f)

                    c_abort_rate_table[rate] /= len(seed_list)
                    print("f rate: {}".format(rate), file=c_f)
                    print(c_abort_rate_table[rate], file=c_f)
                s_f.close()
                c_f.close()
                print("Done!")

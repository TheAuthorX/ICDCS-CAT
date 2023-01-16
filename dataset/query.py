# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# This file implements the SQLs to query the raw Ethereum data from the Google Bigquery API.
# Make sure to config your own GOOGLE_APPLICATION_CREDENTIALS environment!


from google.cloud import bigquery
import csv

client = bigquery.Client()

# the number of effected states = the number of distinct (filtered after the query) log originated addresses + one sender's address

# from the joined TX and log table to select first n contract transactions
subquery_from_contract_TXs = """
    SELECT 
        DISTINCT T.hash, T.from_address, T.gas, T.block_number
    FROM
        `bigquery-public-data.crypto_ethereum.transactions` T 
        INNER JOIN
        `bigquery-public-data.crypto_ethereum.logs` L
        ON
        T.hash=L.transaction_hash
    WHERE
        T.block_number >= 2419265
    ORDER BY
        T.block_number ASC
"""

# from the TX table to select first n transactions. (to_address of the contract create TX is null)
subquery_from_all_TXs = """
    SELECT 
        DISTINCT T.hash, T.from_address, T.to_address, T.gas, T.block_number
    FROM
        `bigquery-public-data.crypto_ethereum.transactions` T
    WHERE
        T.block_number >= 11000000 AND T.to_address IS NOT NULL
    ORDER BY
        T.block_number ASC
"""

# query = f"""
#     SELECT
#         T.hash, T.from_address, L.address, T.gas
#     FROM
#         ({subquery_from_contract_TXs}) T
#         INNER JOIN
#         `bigquery-public-data.crypto_ethereum.logs` L
#         ON
#         T.hash=L.transaction_hash
# """

query = f"""
    SELECT
        T.hash, T.from_address, T.to_address, L.address, T.gas
    FROM
        ({subquery_from_all_TXs}) T
        LEFT JOIN
        `bigquery-public-data.crypto_ethereum.logs` L
        ON
        T.hash=L.transaction_hash
"""

query_job = client.query(query)

iterator = query_job.result()
rows = list(iterator)

# if save_raw_data
f = open('real/raw/raw_data.csv', 'w', encoding='utf-8', newline='')
csv_writer = csv.writer(f)
for row in rows:
    csv_writer.writerow(row)
f.close()

# Transform the rows into a csv file
# transactions = pd.DataFrame(data=[list(x.values()) for x in rows], columns=list(rows[0].keys()))

# Look at the first 10 headlines
# transactions.head(10)

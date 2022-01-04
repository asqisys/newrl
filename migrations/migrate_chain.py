import json
import sqlite3
import hashlib


con = sqlite3.connect('../newrl.db')

cur = con.cursor()

with open('./chain.json', 'r') as read_file:
    chain_data = json.load(read_file)
    print(chain_data)

for block in chain_data:
    encoded_block = json.dumps(block, sort_keys=True).encode()
    hash = hashlib.sha256(encoded_block).hexdigest()

    transactions = block['text']['transactions']
    encoded_block = json.dumps(transactions, sort_keys=True).encode()
    transactions_hash = hashlib.sha256(encoded_block).hexdigest()

    db_block_data = (block['index'], block['timestamp'], block['proof'],
                     block['previous_hash'], hash, transactions_hash)
    cur.execute(f'''INSERT OR IGNORE INTO blocks (block_index, timestamp, proof, previous_hash, hash, transactions_hash) VALUES (?, ?, ?, ?, ?, ?)''', db_block_data)

    block_index = block['index']

    for transaction in transactions:
        specific_data = json.dumps(
            transaction['specific_data']) if 'specific_data' in transaction else ''
        db_transaction_data = (
            block_index,
            transaction['trans_code'],
            transaction['timestamp'],
            transaction['type'],
            transaction['currency'],
            transaction['fee'],
            transaction['descr'],
            transaction['valid'],
            specific_data
        )
        cur.execute(f'''INSERT OR IGNORE INTO transactions
				(block_index, transaction_code, timestamp, type, currency, fee, description, valid, specific_data)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', db_transaction_data)

con.commit()
con.close()

import json
import sqlite3


def download_chain():
    con = sqlite3.connect('../newrl.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    blocks_cursor = cur.execute('SELECT * FROM blocks').fetchall()
    blocks = [dict(ix) for ix in blocks_cursor]
    for idx, block in enumerate(blocks):
        print(block)
        transactions_cursor = cur.execute('SELECT * FROM transactions where block_index=' + str(block['block_index'])).fetchall()
        transactions = [dict(ix) for ix in transactions_cursor]
        block[idx] = {
            'text': {
                'transactions': transactions
            }
        }
    print(blocks)
    
    chain = blocks
    return chain


download_chain()

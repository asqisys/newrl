import json
import sqlite3


def download_state():
    con = sqlite3.connect('../newrl.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    wallets_cursor = cur.execute('SELECT * FROM wallets').fetchall()
    wallets = [dict(ix) for ix in wallets_cursor]

    tokens_cursor = cur.execute('SELECT * FROM tokens').fetchall()
    tokens = [dict(ix) for ix in tokens_cursor]

    balances_cursor = cur.execute('SELECT * FROM balances').fetchall()
    balances = [dict(ix) for ix in balances_cursor]

    state = {
        'wallets': wallets,
        'tokens': tokens,
        'balances': balances,
    }
    return state


download_state()

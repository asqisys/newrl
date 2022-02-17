import json
import sqlite3
import datetime
import time
import hashlib

from ..constants import NEWRL_DB
from .db_updater import *

def update_db_states(cur, newblockindex, transactions):
#    con = sqlite3.connect(NEWRL_DB)
#    cur = con.cursor()
    last_block_cursor = cur.execute(
            f'''SELECT block_index FROM blocks ORDER BY block_index DESC LIMIT 1''')
    last_block = last_block_cursor.fetchone()
    if newblockindex != last_block[0]:
        print("The latest block index does not match given previous index")
        return False
#    latest_index = cur.execute('SELECT MAX(block_index) FROM blocks')
    add_tx_to_block(cur, newblockindex, transactions)
    for transaction in transactions:
        transaction_data = transaction['specific_data']
        while isinstance(transaction_data, str):
            transaction_data = json.loads(transaction_data)

        transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction['trans_code']

        update_state_from_transaction(
            cur,
            transaction['type'],
            transaction_data,
            transaction_code,
            transaction['timestamp']
        )
    return True

def update_state_from_transaction(cur, transaction_type, transaction_data, transaction_code, transaction_timestamp):
    if transaction_type == 1:  # this is a wallet creation transaction
        add_wallet_pid(cur, transaction_data)

    if transaction_type == 2:  # this is a token creation or addition transaction
        add_token(cur, transaction_data, transaction_code)

    if transaction_type == 4 or transaction_type == 5:  # this is a transfer tx
        sender1 = transaction_data['wallet1']
        sender2 = transaction_data['wallet2']

        tokencode1 = transaction_data['asset1_code']
        amount1 = int(transaction_data['asset1_number'] or 0)
        transfer_tokens_and_update_balances(
            cur, sender1, sender2, tokencode1, amount1)

        tokencode2 = transaction_data['asset2_code']
        amount2 = int(transaction_data['asset2_number'] or 0)
        transfer_tokens_and_update_balances(
            cur, sender2, sender1, tokencode2, amount2)

    if transaction_type == 6:    #score update transaction
        personid1 = get_pid_from_wallet (cur, transaction_data['address1'])
        personid2 = get_pid_from_wallet (cur, transaction_data['address2'])
        new_score = transaction_data['new_score']
        tstamp = transaction_timestamp
        update_trust_score(cur, personid1, personid2, new_score, tstamp)

    if transaction_type == 3:    #smart contract transaction
        if not transaction_data['address']: # sc is being set up
            contract = dict(transaction_data['params'])
            funct = "setup"
        else:
            contract = get_contract_from_address(cur, transaction_data['address'])
            funct = transaction_data['function']
        modulename = contract['name']
        module = __import__(modulename)
        sc_class = getattr(module,modulename)
        sc_instance = sc_class(transaction_data['address'])
        funct = getattr(sc_instance, funct)
        funct(cur, transaction_data['params'])
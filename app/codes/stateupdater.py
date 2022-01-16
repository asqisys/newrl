import datetime
import time
import json
from multiprocessing.dummy import current_process
import hashlib

import requests
import sqlite3

from ..constants import NEWRL_DB, NEWRL_PORT, REQUEST_TIMEOUT, STATE_FILE, CHAIN_FILE, MEMPOOL_PATH
from .p2p.peers import get_peers
from .utils import BufferedLog
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager
from .chainscanner import Chainscanner, get_wallet_token_balance

def transfer_tokens_and_update_balances(cur, sender, reciever, tokencode, amount):
    sender_balance = get_wallet_token_balance(sender, tokencode)
    reciever_balance = get_wallet_token_balance(reciever, tokencode)
    sender_balance = sender_balance - amount
    reciever_balance = reciever_balance + amount
    update_wallet_token_balance(cur, sender, tokencode, sender_balance)
    update_wallet_token_balance(cur, reciever, tokencode, reciever_balance)


def update_wallet_token_balance(cur, wallet_address, token_code, balance):
    cur.execute(f'''INSERT OR REPLACE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet_address, token_code, balance))

def update_trust_score(cur, personid1, personid2, new_score, tstamp):
    cur.execute(f'''INSERT OR REPLACE INTO trust_scores
				(src_person_id, , dest_person_id, score, last_time)
				 VALUES (?, ?, ?, ?)''', (personid1, personid2, new_score, tstamp))

def add_wallet_pid(cur, wallet):
    kyc_doc_json = json.dumps(wallet['kyc_docs'])
    data_json = json.dumps(wallet['specific_data'])
    query_params = (wallet['wallet_address'],
                    wallet['wallet_public'],
                    wallet['custodian_wallet'],
                    kyc_doc_json,
                    wallet['ownertype'],
                    wallet['jurisd'],
                    data_json
                    )

    # now checking if this is a linked wallet or new one; for linked, no new personid is created
    linkedstatus =  wallet['specific_data']['linked_wallet'] if 'linked_wallet' in wallet['specific_data'] else False
    if linkedstatus:
        pid_cursor = cur.execute('SELECT person_id FROM person_wallet WHERE wallet_id=?', (wallet['specific_data']['parentaddress'], )).fetchone()
        pid = pid_cursor[0]
        if not pid:
            print("No personid linked to the parentwallet.")
            return False
    else:     #not a linked wallet, so create a new pid and update person table
        hs = hashlib.blake2b(digest_size=20)
        hs.update((wallet['wallet_address']).encode())
        pid = 'pi' + hs.hexdigest()
        query_params=(pid, time.mktime(datetime.datetime.now().timetuple()))
        cur.execute(f'''INSERT OR IGNORE INTO person
                    (person_id, created_time)
                    VALUES (?, ?)''', query_params)

    #for both new and linked wallet, update the wallet table and person_wallet table
    cur.execute(f'''INSERT OR IGNORE INTO wallets
            (wallet_address, wallet_public, custodian_wallet, kyc_docs, owner_type, jurisdiction, specific_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', query_params)

    query_params=(pid, wallet['wallet_address'])
    cur.execute(f'''INSERT OR IGNORE INTO person_wallet
                (person_id, wallet_id)
                VALUES (?, ?)''', query_params)

def add_token(cur, token, txcode = None):
    if 'tokencode' in token:    #creating more of an existing token or tokencode provided by user
        if token['tokencode'] and token['tokencode'] != "0":
            tid = cur.execute('SELECT tokencode FROM tokens WHERE tokencode=?', (token['tokencode'], )).fetchone()
            if tid: #tokencode exists, more of an existing token is being added to the first_owner
                tid = tid[0]
                existingflag = True
            else:
                tid = str(token['tokencode'])    #if provided code does not exist, it is considered new token addition
                existingflag = False
        else:   # mistakenly entered tokencode value as "" or "0" or 0
            tcodenewflag = True
    if 'tokencode' not in token or tcodenewflag:   # new tokencode needs to be created
        hs = hashlib.blake2b(digest_size=20)
        hs.update(txcode.encode())
        tid = 'tk' + hs.hexdigest()
        existingflag = False

    if not existingflag:    # new token to be created
        tokendecimal = token['tokendecimal'] if 'tokendecimal' in token else 0
        tokendecimal = int(tokendecimal)
        token_attributes_json = json.dumps(token['tokenattributes'])
        disallowedjason=json.dumps(token['disallowed'])
        query_params = (
            tid,
            token['tokenname'],
            token['tokentype'],
            token['first_owner'],
            token['custodian'],
            token['legaldochash'],
            token['amount_created'],
            token['value_created'],
            token['sc_flag'],
            disallowedjason,
            txcode,
            tokendecimal,
            token_attributes_json
            )
        cur.execute(f'''INSERT OR IGNORE INTO tokens
            (tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, 
            amount_created, value_created, sc_flag, disallowed, parent_transaction_code, tokendecimal, token_attributes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)

    # now update balance for either case - new token or more of existing created
    if token['amount_created']: # this will be None or 0 for cases where tokens are created with no first owner and 0 amt
        added_balance = int(token['amount_created'])
        current_balance = get_wallet_token_balance(token['first_owner'], tid)
        balance = int(current_balance or 0) + added_balance
        update_wallet_token_balance(
            cur, token['first_owner'], tid, balance)
    return True
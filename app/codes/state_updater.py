import json
import sqlite3
import datetime
import time
import hashlib

from ..constants import NEWRL_DB

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

        if transaction['type'] == 1:  # this is a wallet creation transaction
            add_wallet_pid(cur, transaction_data)

        if transaction['type'] == 2:  # this is a token creation or addition transaction
            add_token(cur, transaction_data, transaction['trans_code'])

        if transaction['type'] == 4 or transaction['type'] == 5:  # this is a transfer tx
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

        if transaction['type'] == 6:    #score update transaction
            personid1 = transaction['specific_data']['personid1']
            personid2 = transaction['specific_data']['personid2']
            new_score = transaction['specific_data']['new_score']
            tstamp = transaction['timstamp']
            update_trust_score(cur, personid1, personid2, new_score, tstamp)

    return True
#    con.commit()
#    con.close()

def transfer_tokens_and_update_balances(cur, sender, reciever, tokencode, amount):
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
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
    # checking if this is a linked wallet or new one; for linked, no new personid is created
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
    cur.execute(f'''INSERT OR IGNORE INTO wallets
            (wallet_address, wallet_public, custodian_wallet, kyc_docs, owner_type, jurisdiction, specific_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', query_params)

    query_params=(pid, wallet['wallet_address'])
    cur.execute(f'''INSERT OR IGNORE INTO person_wallet
                (person_id, wallet_id)
                VALUES (?, ?)''', query_params)

def add_token(cur, token, txcode = None):
    tcodenewflag = False
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
        current_balance = get_wallet_token_balance(cur, token['first_owner'], tid)
        balance = int(current_balance or 0) + added_balance
        update_wallet_token_balance(
            cur, token['first_owner'], tid, balance)
    return True

def get_kyc_doc_hash_json(kyc_docs, kyc_doc_hashes):
    doc_list = []
    for idx, doc in enumerate(kyc_docs):
        doc_list.append({
            'type': doc,
            'hash': kyc_doc_hashes[idx]
        })
    return json.dumps(doc_list)

def get_wallet_token_balance(cur, wallet_address, token_code):
    balance_cursor = cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
                    'address': wallet_address, 'tokencode': token_code})
    balance_row = balance_cursor.fetchone()
    balance = balance_row[0] if balance_row is not None else 0
    return balance

def add_tx_to_block(cur, block_index, transactions):
    print(block_index, transactions)
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
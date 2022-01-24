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
            personid1 = get_pid_from_wallet (cur, transaction['specific_data']['address1'])
            personid2 = get_pid_from_wallet (cur, transaction['specific_data']['address2'])
            new_score = transaction['specific_data']['new_score']
            tstamp = transaction['timestamp']
            update_trust_score(cur, personid1, personid2, new_score, tstamp)

        if transaction['type'] == 3:    #smart contract transaction
            if not transaction['specific_data']['address']: # sc is being set up
                contract = dict(transaction['specific_data']['params'])
                funct = "setup"
            else:
                contract = get_contract_from_address(cur, transaction['specific_data']['address'])
                funct = transaction['specific_data']['function']
            modulename = contract['name']
            module = __import__(modulename)
            sc_class = getattr(module,modulename)
            sc_instance = sc_class(transaction['specific_data']['address'])
            funct = getattr(sc_instance, funct)
            funct(cur, transaction['specific_data']['params'])

    return True
#    con.commit()
#    con.close()

def transfer_tokens_and_update_balances(cur, sender, reciever, tokencode, amount):
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    print("Sender is ",sender  ," and their balance is ", sender_balance)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
    print("Receiver is ",reciever  ," and their balance is ", reciever_balance)
    sender_balance = sender_balance - amount
    reciever_balance = reciever_balance + amount
    print("Amount is ", amount)
    print("Updating sender's balance with ", sender_balance)
    print("Updating reciever's balance with ", reciever_balance)
    update_wallet_token_balance(cur, sender, tokencode, sender_balance)
    update_wallet_token_balance(cur, reciever, tokencode, reciever_balance)
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    print("Sender is ",sender  ," and their balance is ", sender_balance)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
    print("Receiver is ",reciever  ," and their balance is ", reciever_balance)

def update_wallet_token_balance(cur, wallet_address, token_code, balance):
    cur.execute(f'''INSERT OR REPLACE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet_address, token_code, balance))

def update_trust_score(cur, personid1, personid2, new_score, tstamp):
    cur.execute(f'''INSERT OR REPLACE INTO trust_scores
				(src_person_id, dest_person_id, score, last_time)
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
    existingflag = False
    if 'tokencode' in token:    #creating more of an existing token or tokencode provided by user
        if token['tokencode'] and token['tokencode'] != "0" and token['tokencode'] != "":
            tid = cur.execute('SELECT tokencode FROM tokens WHERE tokencode=?', (token['tokencode'], )).fetchone()
            if tid: #tokencode exists, more of an existing token is being added to the first_owner
                tid = tid[0]
                existingflag = True
            else:
                tid = str(token['tokencode'])    #if provided code does not exist, it is considered new token addition
                existingflag = False
        else:   # mistakenly entered tokencode value as "" or "0" or 0
            tcodenewflag = True
            existingflag = False
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
        if token['amount_created']:
            update_wallet_token_balance(
                cur, token['first_owner'], tid, token['amount_created'])

    # now update balance for case of more of existing created
    else:
        added_balance = int(token['amount_created'] or 0)
        current_balance = get_wallet_token_balance(cur, token['first_owner'], tid)
        balance = int(current_balance or 0) + added_balance
        update_wallet_token_balance(
            cur, token['first_owner'], tid, balance)
        if token['amount_created']:
            update_token_amount(cur, tid, token['amount_created'])

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

def update_token_amount(cur, tid, amt):
    tok_val = cur.execute('SELECT tokencode FROM tokens WHERE tokencode = :tokencode', {
                    'tokencode': tid}).fetchone()
    if not tok_val:
        print("Tokencode ", tid, " does not exist.")
        return False
    balance_cursor = cur.execute('SELECT amount_created FROM tokens WHERE tokencode = :tokencode', {
                    'tokencode': tid})
    balance_row = balance_cursor.fetchone()
    cumul_amt = balance_row[0] if balance_row is not None else 0
    cumul_amt = cumul_amt + amt
    cur.execute(f'''INSERT OR REPLACE INTO tokens
				(tokencode, amount_created)
				 VALUES (?, ?)''', (tid, cumul_amt))
    return True

def get_contract_from_address(cur, address):
    contractdata = cur.execute('SELECT * FROM contracts WHERE address = :address', {
                    'address': address}).fetchone()
    if not contractdata:
        print("Contract with address ", address, " does not exist.")
        return {}
    contract = dict(contractdata)
    return contract

def get_pid_from_wallet(cur, walletaddinput):
    pid_cursor = cur.execute('SELECT person_id FROM person_wallet WHERE wallet_id=?', (walletaddinput, ))
    pid = pid_cursor.fetchone()
    if pid is None:
        return False
    return pid[0]
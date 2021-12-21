import json
import sqlite3

def update_db_states(transactions):
    con = sqlite3.connect('newrl.db')
    cur = con.cursor()

    for transaction in transactions:
        if isinstance(transaction['specific_data'], str):
            transaction_data = json.loads(transaction['specific_data'])
        else:
            transaction_data = transaction['specific_data']

        if transaction['type'] == 1:  # this is a wallet creation transaction
            wallet = transaction_data
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

        if transaction['type'] == 2:  # this is a token creation transaction
            token = transaction_data
            token_cursor = cur.execute("SELECT max(tokencode) FROM tokens").fetchone()
            max_token_code = token_cursor[0] if token_cursor is not None else 0
            max_token_code = max_token_code + 1
            token_attributes_json = json.dumps(token['tokenattributes'])
            query_params = (
                max_token_code,
                token['tokenname'],
                token['tokentype'],
                token['first_owner'],
                token['custodian'],
                token['legaldochash'],
                token['amount_created'],
                token['value_created'],
                token['sc_flag'],
                transaction['trans_code'],
                token_attributes_json
            )
            cur.execute(f'''INSERT OR IGNORE INTO tokens
				(tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, 
                amount_created, value_created, sc_flag, parent_transaction_code, token_attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)
            
            balance = token['amount_created']
            update_wallet_token_balance(
                cur, token['first_owner'], max_token_code, balance)

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

    con.commit()
    con.close()


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

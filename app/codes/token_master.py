# Python programm to create object that enables addition of a block

from .utils import get_time_ms
from .db_updater import create_contract_address
import hashlib
import json

def add_token(cur, token, txcode=None):
    '''
    add_token adds a new token type with given value if or if already present adds more value 
    token : contains details like tokencode, tokendecimal, first owner and others
    '''
    tcodenewflag = False
    existingflag = False
    if 'tokencode' in token:  # creating more of an existing token or tokencode provided by user
        if token['tokencode'] and token['tokencode'] != "0" and token['tokencode'] != "":
            tid = cur.execute(
                'SELECT tokencode FROM tokens WHERE tokencode=?', (token['tokencode'], )).fetchone()
            if tid:  # tokencode exists, more of an existing token is being added to the first_owner
                tid = tid[0]
                existingflag = True
            else:
                # if provided code does not exist, it is considered new token addition
                tid = str(token['tokencode'])
                existingflag = False
        else:   # mistakenly entered tokencode value as "" or "0" or 0
            tcodenewflag = True
            existingflag = False
    if 'tokencode' not in token or tcodenewflag:   # new tokencode needs to be created
        randcode = create_contract_address()
        hs = hashlib.blake2b(digest_size=20)
        hs.update(randcode.encode())
        tid = 'tk' + hs.hexdigest()
        existingflag = False

    if not existingflag:    # new token to be created
        tokendecimal = token['tokendecimal'] if 'tokendecimal' in token else 0
        tokendecimal = int(tokendecimal)
        token_attributes_json = json.dumps(token['tokenattributes']) if 'tokenattributes' in token else {}
        disallowed_json = json.dumps(token['disallowed']) if 'disallowed' in token else {}
        query_params = (
            tid,
            token['tokenname'],
            token['tokentype'],
            token['first_owner'],
            token['custodian'],
            token['legaldochash'],
            token['amount_created'],
            token['sc_flag'],
            disallowed_json,
            txcode,
            tokendecimal,
            token_attributes_json
        )
        cur.execute(f'''INSERT OR IGNORE INTO tokens
            (tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, 
            amount_created, sc_flag, disallowed, parent_transaction_code, tokendecimal, token_attributes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)
        if token['amount_created']:
            update_wallet_token_balance(
                cur, token['first_owner'], tid, token['amount_created'])

    # now update balance for case of more of existing created
    else:
        if token['first_owner'] and token['amount_created']:
            added_balance = int(token['amount_created'] or 0)
            current_balance = get_wallet_token_balance(
                cur, token['first_owner'], tid)
            balance = int(current_balance or 0) + added_balance
            update_wallet_token_balance(
                cur, token['first_owner'], tid, balance)
            update_token_amount(cur, tid, token['amount_created'])

    return True

def token_transfer(cur,transaction_data):
    '''
    token_transfer performs transfer of tokens from one wallet to others based on type one way or two way
    transaction_data : contains details of wallets and owners and asset codes along with quantity
    '''
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


#token util methods

def transfer_tokens_and_update_balances(cur, sender, reciever, tokencode, amount):
    '''
    transfer_tokens_and_update_balances updates balances of sender and receiver for that token code and amount
    '''
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    print("Sender is ", sender, " and their balance is ", sender_balance)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
    print("Receiver is ", reciever, " and their balance is ", reciever_balance)
    sender_balance = sender_balance - amount
    reciever_balance = reciever_balance + amount
    print("Amount is ", amount)
    print("Updating sender's balance with ", sender_balance)
    print("Updating reciever's balance with ", reciever_balance)
    update_wallet_token_balance(cur, sender, tokencode, sender_balance)
    update_wallet_token_balance(cur, reciever, tokencode, reciever_balance)
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    print("Sender is ", sender, " and their balance is ", sender_balance)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
    print("Receiver is ", reciever, " and their balance is ", reciever_balance)

def get_wallet_token_balance(cur, wallet_address, token_code):
    '''
    get_wallet_token_balance returns given wallet balance
    '''
    balance_cursor = cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
        'address': wallet_address, 'tokencode': token_code})
    balance_row = balance_cursor.fetchone()
    balance = balance_row[0] if balance_row is not None else 0
    return balance    

def update_token_amount(cur, tid, amt):
    '''
    update_token_amount updates token amount for given tid
    tid : token id 
    '''
    if not amt:
        print("Nothing to add.")
        return True
    tok_val = cur.execute('SELECT tokencode FROM tokens WHERE tokencode = :tokencode', {
        'tokencode': tid}).fetchone()
    if not tok_val:
        print("Tokencode ", tid, " does not exist.")
        return False
    balance_cursor = cur.execute('SELECT amount_created FROM tokens WHERE tokencode = :tokencode', {
        'tokencode': tid})
    balance_row = balance_cursor.fetchone()
    if balance_row:
        cumul_amt = int(balance_row[0]) if balance_row[0] else 0
    else:
        cumul_amt = int(0)
    cumul_amt = cumul_amt + amt
#    cur.execute(f'''INSERT OR REPLACE INTO tokens
#				(tokencode, amount_created)
#				 VALUES (?, ?)''', (tid, cumul_amt))
    cur.execute(
        f'''UPDATE tokens SET amount_created=? WHERE tokencode=?''', (cumul_amt, tid))

    return True    

def update_wallet_token_balance(cur, wallet_address, token_code, balance):
    '''
    update_wallet_token_balance updates walleta balance with given amount
    '''
    cur.execute(f'''INSERT OR REPLACE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet_address, token_code, balance))    
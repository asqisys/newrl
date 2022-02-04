import json
#from ossaudiodev import SNDCTL_FM_LOAD_INSTR
import importlib

from .statemanager import add_token, add_tx_to_block, add_wallet_pid, get_contract_from_address, get_pid_from_wallet, transfer_tokens_and_update_balances, update_trust_score

from ..constants import NEWRL_DB

def update_db_states(cur, newblockindex, transactions):
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

        if transaction['type'] == 1:  # this is a wallet creation transaction
            add_wallet_pid(cur, transaction_data)

        if transaction['type'] == 2:  # this is a token creation or addition transaction
            add_token(cur, transaction_data, transaction_code)

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
        #    continue
            funct = transaction['specific_data']['function']
            if funct == "setup": # sc is being set up
                contract = dict(transaction['specific_data']['params'])
                transaction['specific_data']['params']['parent']= transaction['trans_code']
            else:
                contract = get_contract_from_address(cur, transaction['specific_data']['address'])
            module = importlib.import_module(".codes.contracts."+contract['name'],package="app")
            sc_class = getattr(module, contract['name'])
            sc_instance = sc_class(transaction['specific_data']['address'])
        #    sc_instance = nusd1(transaction['specific_data']['address'])
            funct = getattr(sc_instance, funct)
            funct(cur, transaction['specific_data']['params'])

    return True


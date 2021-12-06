# Create an object for tokens on blockchain Newrl

import datetime

from .transactionmanager import Transactionmanager

def create_token_transaction(token_data):
    transaction = {
        'timestamp': str(datetime.datetime.now()),
        'type': 2,
        'currency': "INR",
        'fee': 0.0,
        'descr': "New token creation",
        'valid': 1,
        'block_index': 0,
        'specific_data': token_data
    }

    trans = Transactionmanager()
    transaction_data = {'transaction': transaction, 'signatures': []}
    trans.transactioncreator(transaction_data)
    transaction_file = trans.dumptransaction()
    return transaction_file

# code for managing trust scores between two persons
import datetime

from .transactionmanager import Transactionmanager


def update_score_transaction(personid1, address1, personid2, address2, new_score):
    transaction = {
        'timestamp': str(datetime.datetime.now()),
        'type': 6,
        'currency': "INR",
        'fee': 0.0,
        'descr': "Score update",
        'valid': 1,
        'block_index': 0,
        'specific_data': {"personid1": personid1,
                          "address1": address1,
                          "personid2": personid2,
                          "address2": address2,
                          "new_score": new_score
                          }
    }

    trans = Transactionmanager()
    transaction_data = {'transaction': transaction, 'signatures': []}
    trans.transactioncreator(transaction_data)
    transaction_file = trans.save_transaction_to_mempool()
    return transaction_file

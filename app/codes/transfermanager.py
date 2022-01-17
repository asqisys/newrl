import json
import datetime
import uuid

from ..constants import MEMPOOL_PATH, STATE_FILE, TMP_PATH
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager


class Transfermanager(Transactionmanager):
    def __init__(self, transfer_data):
        Transactionmanager.__init__(self)
        self.transaction = {
                "timestamp": str(datetime.datetime.now()),
                "trans_code": uuid.uuid4().hex,
                "type": int(transfer_data['transfer_type']),
                "currency": "INR",
                "fee": 0.0,
                "descr": "",
                "valid": 1,
                "specific_data": transfer_data
            }

    def techvalid(self):
        return True
        # add more constraints here later

    def loadandcreate(self):
        if self.techvalid():
            full_transaction = {
                'transaction': self.transaction,
                'signatures': self.signatures
            }
            return full_transaction
            # file = self.dumptransaction()
            # with open(file) as f:
            #     transaction = json.load(f)
            #     return transaction

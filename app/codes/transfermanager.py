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

    def loadandcreate(self, transfer_data=None):
    #    self.transferdata = transfer_data
    #    tdataall = {"transaction":self.transferdata, "signatures":[]} 
        tdatawithcode = self.transactioncreator(self.transferdata)
        if self.techvalid():
            self.dumptransaction()
        return tdatawithcode

import json
import datetime
import uuid

from ..constants import MEMPOOL_PATH, STATE_FILE, TMP_PATH
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager


class Transfermanager(Transactionmanager):
    def __init__(self, transfer_data):
        Transactionmanager.__init__(self)
        self.transaction = transfer_data['transaction']
        self.fulltrandata = transfer_data

    def techvalid(self):
        return True
        # add more constraints here later

    def loadandcreate(self, transfer_data=None):
    #    self.transferdata = transfer_data
    #    tdataall = {"transaction":self.transferdata, "signatures":[]} 
        tdatawithcode = self.transactioncreator(self.fulltrandata)
    #    if self.techvalid():
    #        self.dumptransaction()
        return tdatawithcode

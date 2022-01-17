from ..constants import MEMPOOL_PATH, STATE_FILE
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager


class Transfermanager(Transactionmanager):
    def __init__(self, transfer_data):
        Transactionmanager.__init__(self)
        if transfer_data:
            self.transferdata = transfer_data
        else:
            self.transaction['type'] = 4
            self.transaction['specific_data'] = {
                'asset1_code': 0,
                'asset2_code': 0,
                'wallet1': None,
                'wallet2': None,
                'asset1_number': 0,
                'asset2_number': 0,
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
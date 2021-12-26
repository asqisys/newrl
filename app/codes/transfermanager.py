from ..constants import MEMPOOL_PATH, STATE_FILE
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager


class Transfermanager(Transactionmanager):
    #	def Transactionmanager.__init__(self, transferfile=None):
    def __init__(self, transferfile=None):
        Transactionmanager.__init__(self)
#		self.tokenrecordsfile="all_tokens.json";
        if transferfile:
            self.transferdata = self.loadtransaction(transferfile)
            print("Loaded transfer transaction from ", transferfile)
#		if not True:
#			a=1
        else:
            self.transaction['type'] = 4
            self.transaction['specific_data'] = {'asset1_code': 0,
                                                 'asset2_code': 0,
                                                 'wallet1': None,
                                                 'wallet2': None,
                                                 'asset1_number': 0,
                                                 'asset2_number': 0, }

    def techvalid(self):
        return True
        # add more constraints here later

    def loadandcreate(self, transferfile=None):
        if not transferfile:
            print("Nothing to load, exiting")
            return False
        self.transferdata = self.loadtransaction(transferfile)
        print("Loaded transfer transaction from ", transferfile)
        # need to load signatures as well later
        if self.techvalid():
            self.dumptransaction(transferfile)

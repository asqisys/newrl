import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from codes.blockchain import Blockchain
from codes.transactionmanager import Transactionmanager

class Transfermanager(Transactionmanager):
#	def Transactionmanager.__init__(self, transferfile=None):
	def __init__(self,mempool="data/mempool/",statefile="./data/common/state.json",transferfile=None):
		Transactionmanager.__init__(self,mempool,statefile);
#		self.tokenrecordsfile="data/common/all_tokens.json";
		if transferfile:
			self.transferdata=self.loadtransaction(transferfile);
			print("Loaded transfer transaction from ",transferfile)
#		if not True:
#			a=1
		else:
			self.transaction['type']=4;
			self.transaction['specific_data']={'asset1_code':0,
							'asset2_code':0,
							'wallet1':None,
							'wallet2':None,
							'asset1_number':0,
							'asset2_number':0,}
	def techvalid(self):
		return True
		# add more constraints here later

	def loadandcreate(self,transferfile=None):
		if not transferfile:
			print("Nothing to load, exiting")
			return False
		self.transferdata=self.loadtransaction(transferfile);
		print("Loaded transfer transaction from ",transferfile)
		#need to load signatures as well later
		if self.techvalid():
			self.dumptransaction(transferfile)

def main():
	parser = OptionParser();
	parser.add_option("-t", "--transferfile", dest="transferfile",default="transferex.json",help="Input transferfile. default - transferex.json");
	parser.add_option("-m", "--mempool", dest="mempool",default="data/mempool/",help="Mempool directory. default - data/mempool/");
	parser.add_option("-s", "--statefile", dest="statefile",default="data/common/state.json",help="Input statefile. default - data/common/state.json");
	(options, args) = parser.parse_args()
#	newtoken=Transfermanager(options.tokenfile)
	newtransfer=Transfermanager(options.mempool, options.statefile)
	newtransfer.dumptransaction('transferex.json')
#	print(newtoken.transaction)

if __name__ == "__main__":
	main();


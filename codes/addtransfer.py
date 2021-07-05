import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from codes.blockchain import Blockchain
from codes.transfermanager import Transfermanager

def main():
	parser = OptionParser();
	parser.add_option("-t", "--transferfile", dest="transferfile",default=None,help="Input transferfile. default - None");
	parser.add_option("-m", "--mempool", dest="mempool",default="./mempool/",help="Mempool directory. default - ./mempool/");
	parser.add_option("-s", "--statefile", dest="statefile",default="state.json",help="Input statefile. default - state.json");
	(options, args) = parser.parse_args()
#	newtoken=Transfermanager(options.tokenfile)
	newtransfer=Transfermanager(options.mempool,options.statefile,options.transferfile)
#	newtransfer.dumptransaction('temptrans.json')
	newtransfer.loadandcreate(options.transferfile)
#	print(newtoken.transaction)

def create_transfer(transferfile=None, mempool="./mempool/", statefile="state.json"):
	newtransfer=Transfermanager(mempool,statefile,transferfile)
#	newtransfer.dumptransaction('temptrans.json')
	newtransfer.loadandcreate(transferfile)

if __name__ == "__main__":
	main();


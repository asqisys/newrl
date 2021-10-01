# Python programm to use tokenmanager.py to add tokens using files etc

import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from codes.blockchain import Blockchain
from codes.tokenmanager import Tokenmanager

# def main():
def add_token(tokenfile="data/tmp/tokennew.json", mempool="data/mempool/", statefile="data/common/state.json"):
	# parser = OptionParser();
	# parser.add_option("-t", "--tokenfile", dest="tokenfile",default="data/tmp/tokennew.json",help="Input tokenfile. default - data/tmp/tokennew.json");
	# parser.add_option("-m", "--mempool", dest="mempool",default="data/mempool/",help="Mempool directory. default - data/mempool/");
	# parser.add_option("-s", "--statefile", dest="statefile",default="data/common/state.json",help="Input statefile. default - data/common/state.json");
	# (options, args) = parser.parse_args()
	newtoken=Tokenmanager()
	print(newtoken.tokendata)
	print(newtoken.istokeninrecords())
#	newtoken.dumptokendata("data/tmp/firsttoken.json")
	transaction_file = newtoken.loadandcreate(tokenfile,mempool,statefile)
	newtoken.dumptokendata("data/tmp/firsttoken.json")
	return transaction_file
#	cs=chainscanner(options.tokenfile)
#	print(cs.chainlength)
#	print(cs.gettransactions(3))

if __name__ == "__main__":
	main();


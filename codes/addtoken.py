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
def add_token(tokenfile="tokennew.json", mempool="./mempool/", statefile="state.json"):
	# parser = OptionParser();
	# parser.add_option("-t", "--tokenfile", dest="tokenfile",default="tokennew.json",help="Input tokenfile. default - tokennew.json");
	# parser.add_option("-m", "--mempool", dest="mempool",default="./mempool/",help="Mempool directory. default - ./mempool/");
	# parser.add_option("-s", "--statefile", dest="statefile",default="state.json",help="Input statefile. default - state.json");
	# (options, args) = parser.parse_args()
	newtoken=Tokenmanager()
	print(newtoken.tokendata)
	print(newtoken.istokeninrecords())
#	newtoken.dumptokendata("firsttoken.json")
	newtoken.loadandcreate(tokenfile,mempool,statefile)
	newtoken.dumptokendata("firsttoken.json")
	return "firsttoken.json"
#	cs=chainscanner(options.tokenfile)
#	print(cs.chainlength)
#	print(cs.gettransactions(3))

if __name__ == "__main__":
	main();


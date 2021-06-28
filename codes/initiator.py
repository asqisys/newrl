# Python programm to create the genesis block with a given chain creator wallet address

import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from blockchain import Blockchain

def main():
	parser = OptionParser()
#	parser.add_option("-g", "--genfile", dest="genfile",default="genesis.json",help="Input genesisfile. default - genesis.json");
	parser.add_option("-c", "--chainfile", dest="chainfile",default="chain.json",help="Input chainfile. default -chain.json")
	parser.add_option("-s", "--statefile", dest="statefile",default="state.json",help="Input statefile. default - state.json")

	(options, args) = parser.parse_args()
	#blockchain = Blockchain("inginesis.json")
	if not options.chainfile or not options.statefile:
		print("No chainfile or statefile specified, exiting.")
	#	exit()
		return False

	blockchain = Blockchain(options.chainfile)
	statefile=options.statefile
	print("Loaded chain validity status : ",blockchain.chain_valid(blockchain.chain))

	empty=[]
	with open("empty.json","w") as writefile:
		json.dump(empty, writefile)

	if not os.path.exists("all_wallets.json"):
	#	shutil.copy("creatorwalletdata.json","all_wallets.json")
		print("all_wallets.json does not exist, creating. Signing won't work till valid addresses added to it.")
		allw=[]
		with open("all_wallets.json","w") as writefile:
			json.dump(allw,writefile)
	else:
		print("all_wallets.json already exists. Signing will work for addresses in it.")

	if not os.path.exists("all_tokens.json"):
		shutil.copy("empty.json","all_tokens.json")
	else:
		print("all_tokens.json already exists.")

	print("Making mempool, incltranspool and statearchive directories")
	if not os.path.exists("./mempool/"):
		os.mkdir("./mempool/")
	else:
		print("WRN: Mempool already exists, beware of possible errors")
	if not os.path.exists("./incltranspool/"):
		os.mkdir("./incltranspool/")
	else:
		print("WRN: Incltranspool already exists, beware of possible errors")
	if not os.path.exists("./statearchive/"):
		os.mkdir("./statearchive/")		
	else:
		print("WRN: statearchive  already exists, beware of possible errors")

if __name__ == "__main__":
	main();

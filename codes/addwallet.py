# Python programm to create object that enables addition of a block

import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from blockchain import Blockchain
from kycwallet import Walletmanager

def main():
	parser = OptionParser();
	parser.add_option("-w", "--walletfile", dest="walletfile",default="all_wallets.json",help="Wallet recordfile. default - all_wallets.json");
	parser.add_option("-i", "--idfile", dest="idfile",default=None,help="Id file in KYC,  default - None");
	parser.add_option("-a", "--adfile", dest="adfile",default=None,help="postal address file in KYC,  default - None");
	parser.add_option("-c", "--kyccust", dest="kyccust",default="0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42",help="KYC custodian address,  default - 0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42");
	(options, args) = parser.parse_args()
	wm=Walletmanager(options.walletfile)
#	walletdata=wm.wallet_maker()
#	files=["currentstate.txt","policy.txt"]
	files=[]
	files.append(options.idfile)
	files.append(options.adfile)
	kycdocs=[1,2]
	specific_data=[]
	kyccust=options.kyccust
#	files=["currentstate.txt","policy.txt"]
	newaddress=wm.wallet_maker(kyccust,kycdocs,files,1,2,specific_data)
#	wm.kycdocslinker(files,kycdocs)
	wm.walletlistupdater()
#	print(cs.chainlength)
#	print(cs.gettransactions(3))
#	print(wm.wallet)

if __name__ == "__main__":
	main();


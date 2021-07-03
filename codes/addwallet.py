# Python programm to create object that enables addition of a block

import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from codes.blockchain import Blockchain
from codes.kycwallet import Walletmanager

def add_wallet(idfile, adfile, 
				kyccust="0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42", walletfile="all_wallets.json",
				ownertype=1,
				jurisdiction=2,
				outputfile="newwallet.json"):
	wm=Walletmanager(walletfile)
#	walletdata=wm.wallet_maker()
	files=[]
	files.append(idfile)
	files.append(adfile)
	kycdocs=[1,2]
	specific_data=[]
	kyccust=kyccust
	transferfile, keysdata=wm.wallet_maker(kyccust,kycdocs,files,ownertype,jurisdiction,specific_data)
#	wm.kycdocslinker(files,kycdocs)
	with open(keysdata[0]['address'] + "_wallet.json","w") as writefile:
		json.dump(keysdata,writefile)
	wm.walletlistupdater()
	return transferfile

def main():
	parser = OptionParser();
	parser.add_option("-w", "--walletfile", dest="walletfile",default="all_wallets.json",help="Wallet recordfile. default - all_wallets.json");
	parser.add_option("-i", "--idfile", dest="idfile",default=None,help="Id file in KYC,  default - None");
	parser.add_option("-a", "--adfile", dest="adfile",default=None,help="postal address file in KYC,  default - None");
	parser.add_option("-c", "--kyccust", dest="kyccust",default="0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42",help="KYC custodian address,  default - 0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42");
	parser.add_option("-o", "--outputfile", dest="outputfile",default="newwallet.json",help="New wallet keys file. default - newwallet.json");
	parser.add_option("-y", "--ownertype", dest="ownertype",default=1,help="Ownertype,  default - 1 i.e. individual");
	parser.add_option("-j", "--jurisd", dest="jurisd",default=2,help="Ownertype,  default - 2 i.e. India");
	(options, args) = parser.parse_args()
	wm=Walletmanager(options.walletfile)
#	walletdata=wm.wallet_maker()
	files=[]
	files.append(options.idfile)
	files.append(options.adfile)
	kycdocs=[1,2]
	specific_data=[]
	kyccust=options.kyccust
	newaddress=wm.wallet_maker(kyccust,kycdocs,files,options.ownertype,options.jurisd,specific_data)
#	wm.kycdocslinker(files,kycdocs)
	with open(options.outputfile,"w") as writefile:
		json.dump(newaddress,writefile)
	wm.walletlistupdater()

if __name__ == "__main__":
	main();


# program to create and manage objects for wallets
import codecs
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import json
import datetime
import binascii
import base64

from starlette.responses import FileResponse
from codes.transactionmanager import Transactionmanager
import base64
from optparse import OptionParser

#this below one is useful for signing-time check
def addresschecker(transaction, address):
#	trans=trandata['transaction']
#	signatures = trandata['signatures']
	validadds=getvalidadds(transaction)
	print(validadds)
	for add in validadds:
		if add==address:
			print("The address ",address," is authorised to sign this transaction.")
			return True
		# did not find the address in the validadds
	print("The address ",address," is not authorised to sign this transaction.")
	return False

#use the below one to get all authorized addresses that can sign a transaction
def getvalidadds(transaction):
	trans=transaction
	ttype=trans['type']
	validadds=[]
	if ttype==1:	#wallet creation, custodian needs to sign
		validadds.append(trans['specific_data']['custodian_wallet'])
	if ttype==2:	# token creation, custodian needs to sign
		validadds.append(trans['specific_data']['custodian'])
	if ttype==4:	# two way transfer; both senders need to sign
		validadds.append(trans['specific_data']['wallet1'])
		validadds.append(trans['specific_data']['wallet2'])
	if ttype==5:	# one way transfer; only sender1 is needed to sign
		validadds.append(trans['specific_data']['wallet1'])
	return validadds

#use the below for validator
def checkaddress(transaction, signatures):
	validadds=getvalidadds(transaction)
#	signatures = trandata['signatures']
	validsigns=1
	sumonevalids=0
	for signature in signatures:
		onesignvalid=0
		for address in validadds:
			if signature['wallet_address']==address:	#the signatures includes a valid address
				print("The address ",signature['wallet_address']," in signature is authorised to sign this transaction.")
				onesignvalid=1
		if not onesignvalid:
			print("The address ",signature['wallet_address']," in signature is not authorised to sign this transaction.")
		validsigns=validsigns*onesignvalid
		sumonevalids+=onesignvalid
	if validsigns and sumonevalids:		#adding sum to guard against the case where there are no signatures at all
		return True
	else:
		return False

def main():
	parser = OptionParser()
	parser.add_option("-t", "--transfile", dest="transfile",default=None,help="Input transactionfile. default - None");
	parser.add_option("-m", "--mempool", dest="mempool",default="./mempool/",help="Mempool directory. default - ./mempool/");
	parser.add_option("-w", "--walletfile", dest="walletfile",default="all_wallets.json",help="Wallet recordfile. default - all_wallets.json");
	parser.add_option("-a", "--address", dest="address",default=None,help="String of address. default - None");
#	parser.add_option("-i", "--itpool", dest="itpool",default="./incltranspool/",help="Included transactions directory. default - ./incltranspool/");
#	parser.add_option("-s", "--state", dest="state",default="state.json",help="Statefile. default - state.json");

	(options, args) = parser.parse_args()
#	wallet=Walletmanager(option.walletfile);
#	wallet.iswalletlisted()
	pvtkeybytes=None
	pubkeybytes=None
	with open(options.walletfile, 'r') as file:
		data=json.load(file)
	for walletdata in data:
		if walletdata['address']==options.address:
			pvtkeybytes=base64.b64decode(walletdata['private'])
			pubkeybytes=base64.b64decode(walletdata['public'])
	if not pvtkeybytes:
		print("No private key found for the address")
		return False

	tm=Transactionmanager()
	tm.loadtransactionpassive(options.transfile)
#	print("Current signatures are ",tm.signatures)
	if not addresschecker(tm.transaction,options.address):
		return False

	signtransbytes=tm.signtransaction(pvtkeybytes,options.address)
	print("signed msg signature is:",signtransbytes," and address is ",options.address)
	signtrans=base64.b64encode(signtransbytes).decode('utf-8')
#	print("storing this in encoded form is:",signtrans)
	if signtrans:
		tm.dumptransaction(options.transfile)
		print("Successfully signed the transaction and updated its signatures data.")
	#	print("Signatures are")
		print("Status of signing: ",tm.verifysign(signtrans,pubkeybytes,options.address))
	else:
		print("Signing failed. No change made to transaction's signature data")

if __name__ == "__main__":
	main();



def sign(address, transfile=None, walletfile="all_wallets.json", mempool="./mempool/"):
	# parser = OptionParser()
	# parser.add_option("-t", "--transfile", dest="transfile",default=None,help="Input transactionfile. default - None");
	# parser.add_option("-m", "--mempool", dest="mempool",default="./mempool/",help="Mempool directory. default - ./mempool/");
	# parser.add_option("-w", "--walletfile", dest="walletfile",default="all_wallets.json",help="Wallet recordfile. default - all_wallets.json");
	# parser.add_option("-a", "--address", dest="address",default=None,help="String of address. default - None");
#	parser.add_option("-i", "--itpool", dest="itpool",default="./incltranspool/",help="Included transactions directory. default - ./incltranspool/");
#	parser.add_option("-s", "--state", dest="state",default="state.json",help="Statefile. default - state.json");

	# (options, args) = parser.parse_args()
#	wallet=Walletmanager(option.walletfile);
#	wallet.iswalletlisted()
	pvtkeybytes=None
	pubkeybytes=None
	with open(walletfile, 'r') as file:
		data=json.load(file)
	for walletdata in data:
		if walletdata['address']==address:
			pvtkeybytes=base64.b64decode(walletdata['private'])
			pubkeybytes=base64.b64decode(walletdata['public'])
	if not pvtkeybytes:
		print("No private key found for the address")
		return False

	tm=Transactionmanager()
	tm.loadtransactionpassive(transfile)
#	print("Current signatures are ",tm.signatures)
	if not addresschecker(tm.transaction,address):
		return False

	signtransbytes=tm.signtransaction(pvtkeybytes,address)
	print("signed msg signature is:",signtransbytes," and address is ",address)
	signtrans=base64.b64encode(signtransbytes).decode('utf-8')
#	print("storing this in encoded form is:",signtrans)
	if signtrans:
		tm.dumptransaction(transfile)
		print("Successfully signed the transaction and updated its signatures data.")
	#	print("Signatures are")
		sign_status = tm.verifysign(signtrans,pubkeybytes,address)
		print("Status of signing: ", sign_status)
		return FileResponse(transfile)
		# return sign_status
	else:
		print("Signing failed. No change made to transaction's signature data")
		return None

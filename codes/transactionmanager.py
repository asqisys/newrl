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

class Transactionmanager:
	def __init__(self, mempool="data/mempool/",statefile="./data/common/state.json"):
#		self.public=
#		hs=hashlib.blake2b()
		self.transaction= {'timestamp': str(datetime.datetime.now()),
					'trans_code':"0000",
					'type': 0, 
					'currency':"INR", 
					'fee':0.0 , 
					'descr':None,
					'valid':1, 
			#		'block_index': 0,
					'specific_data':{}
#					"custodian_wallet":None,
#					"kyc_docs":[],
#					"kyc_doc_hashes":[],
#					"wallet_address":[],
					}

		self.signatures=[]
	#	self.validations=[]
		self.mempool=mempool		#memory pool of transactions waiting to be validated and included in block
		self.itpool="data/incltranspool/"		#pool of included transactions
		self.statefile=statefile
		self.validity=0

	def getvalidadds(self):
		trans=self.transaction
		ttype=trans['type']
		validadds=[]
		if ttype==1:    #wallet creation, custodian needs to sign
			validadds.append(trans['specific_data']['custodian_wallet'])
		if ttype==2:    # token creation, custodian needs to sign
			validadds.append(trans['specific_data']['custodian'])
		if ttype==4:    # two way transfer; both senders need to sign
			validadds.append(trans['specific_data']['wallet1'])
			validadds.append(trans['specific_data']['wallet2'])
		if ttype==5:    # one way transfer; only sender1 is needed to sign
			validadds.append(trans['specific_data']['wallet1'])
		return validadds

	def transactioncreator(self,tran_data_all):
	#standard data concerns static fields, specific data covers fields that are type specific
		tran_data=tran_data_all['transaction'];
		if not tran_data['timestamp']:
			self.transaction['timestamp']= str(datetime.datetime.now())
		else:
			self.transaction['timestamp']=tran_data['timestamp'];
		
		self.transaction['type']=tran_data['type'];
		self.transaction['currency']=tran_data['currency'];
		self.transaction['fee']=tran_data['fee'];
		self.transaction['descr']=tran_data['descr'];
	#	self.transaction['valid']=tran_data['valid'];
		self.transaction['valid']=1	#default at creation is unverified
	##	self.transaction['block_index']=tran_data['block_index'];
#		if standard_data['type']==1: #this is wallet creation
#			self.transaction['custodian_wallet']=specific_data['custodian_wallet'];
#			self.transaction['kyc_docs']=specific_data['kyc_docs'];
#			self.transaction['kyc_doc_hashes']=specific_data['kyc_doc_hashes'];
#			self.transaction['wallet_address']=specific_data['wallet_address'];
		self.transaction['specific_data']=tran_data['specific_data'];
		trstr=json.dumps(self.transaction).encode()
#		encstr=codecs.encode(trstr, 'hex')
		hs=hashlib.blake2b(digest_size=20)
		hs.update(trstr)
		self.transaction['trans_code']=hs.hexdigest()
	#	print("tcode while creating is ",self.transaction['trans_code'])
		self.signatures=tran_data_all['signatures']
	#	self.validations=tran_data_all['validations']
		transaction_all={'transaction':self.transaction,'signatures':self.signatures}
		return transaction_all

	def loadtransactionpassive(self,file):	#this just loads the trasnactions passively, no change
		transactiondata={}
		with open(file,"r") as readfile:
			print("Now reading from ",file)
			trandata=json.load(readfile);
		self.transaction=trandata['transaction']
		self.signatures=trandata['signatures']
		return trandata

	def loadtransaction(self,file):	#this loads a transaction and creates a new trnsaction id
		transactiondata={}
		with open(file,"r") as readfile:
			print("Now reading from ",file)
			trandata=json.load(readfile);
		newtrandata=self.transactioncreator(trandata)
#		transactiondata['transaction'] = self.transactioncreator(trandata)['transaction'];
#		transactiondata['signatures'] = self.transactioncreator(trandata)['signatures'];
#		transactiondata['transaction'] = trandata['transaction']
#		transactiondata['signatures'] = trandata['signatures']
		return newtrandata
	
	def dumptransaction(self,file=None):	#dumps active transaction into a stated file or in mempool by default
		ts=self.transaction['timestamp'];
		if not ts:
			ts=str(datetime.datetime.now());
		if not file:
			file=self.mempool+"transaction-"+str(self.transaction['type'])+"-"+ts[0:10]+"-"+ts[-6:]+".json"
	#	print("tcode while writing is ", self.transaction['trans_code'])
	#	print(self.transaction)
	#	transaction_all={'transaction':self.transaction,'signatures':self.signatures,'validations':self.validations}
		transaction_all={'transaction':self.transaction,'signatures':self.signatures}
	#	print(self.signatures)
		with open(file,"w") as writefile:
		#	json.dump(self.transaction, writefile);
			json.dump(transaction_all, writefile);
			print("Wrote to ",file)
		return file

	def signtransaction(self,keybytes,address):	#this takes keybytes and not binary string and not base64 string
		msg=json.dumps(self.transaction).encode();
		sk=ecdsa.SigningKey.from_string(keybytes, curve=ecdsa.SECP256k1)
		msgsignbytes=sk.sign(msg)
		msgsign=base64.b64encode(msgsignbytes).decode('utf-8')
		self.signatures.append({'wallet_address':address,'msgsign':msgsign})
	#	print("signed message ",msgsign,"and the key used was",keybytes)
		return sk.sign(msg)

	def verifysign(self,sign_trans,pubkeybytes,address):
	### the pubkey above is in bytes form
	#	print("using this pubkey to verify:",pubkeybytes)
		sign_trans_bytes=base64.decodebytes(sign_trans.encode('utf-8'))
		vk=ecdsa.VerifyingKey.from_string(pubkeybytes, curve=ecdsa.SECP256k1)
		message=json.dumps(self.transaction).encode();
	#	print("Sign validity: ",vk.verify(sign_trans,message))
	#	print("message is", message)
	#	print("sign_trans_byets are ",sign_trans_bytes)
		return vk.verify(sign_trans_bytes,message)
	
	def verifytransigns(self):
		#need to add later a check for addresses mentioned in the transaction (vary by type) and the signing ones
	#	addresses=[];
	#	wfile="./tmpallw.json"
	#	wfile="./data/common/all_wallets.json"
		with open(self.statefile,"r") as statefile:
	#	with open(wfile,"r") as statefile:
			state=json.load(statefile);
		allwallets=state["all_wallets"]
		validadds=self.getvalidadds()
		addvaliditydict={}
		for valadd in validadds:
			addvaliditydict[valadd]=False;
	#	allwallets=state
		prodflag=1
		for signature in self.signatures:
			signaddress=signature['wallet_address'];
	#		print("signaddress from signature: ",signaddress)
			addressvalidity=0
			for valadd in validadds:
				if signaddress==valadd:	#the signature is of a relevant address for that transaction
					addressvalidity=1
			if not addressvalidity:
				print("Signature with address ",signaddress," is not relevant for this transaction.")
				continue
			msgsign=signature['msgsign']
			pubkey=None
			for wallet in allwallets:
		#		address=wallet['wallet_address']
				address=wallet['wallet_address']
		#		print("address is ",address," and signaddress was ",signaddress)
				if address==signaddress:
					pubkey=wallet['wallet_public']	#this is in base64 coded form, not bytes, not binary string
			#		print("found this pubkey:", pubkey)	
	#		print("encoded pubkey from json file: ",pubkey)
			pubkeybytes=base64.b64decode(pubkey)	#here we decode the base64 form to get pubkeybytes
		#	print("decoded bytes of pubkey",pubkeybytes)
	#		print("now verifying ",msgsign)
			if not self.verifysign(msgsign,pubkeybytes,signaddress):
				print("Signature for address ",signaddress," is invalid")
				prodflag=prodflag*0
				addvaliditydict[signaddress]=False	#making doubly sure
				return False
			else:
				addvaliditydict[signaddress]=True	#for a valid address the signature is found
				prodflag=prodflag*1
		if prodflag:
			print("All provided signatures of the message valid; still need to check if all required ones are provided")
		#	return True
		else:
			print("Some of the provided signatures not valid")
		#	return False
		#now checking if signatures for all valid addresses are covered
		validsignspresent=0
		for valadd in validadds:
			if addvaliditydict[valadd]:
				validsignspresent+=1;
			else:
				print("Either couldn't find signature or found invalid signature for ",valadd)
			#	valaddsignpresent=valaddsignpresent*0;	#any one signaure not being present will throw an error
		if prodflag and validsignspresent>=len(validadds):
			print("All provided signatures valid and all required signatures provided")
			return True
		else:
			print("Either some signatures invalid or some required ones missing")
			return False

#	def techvalidator(self):
		#write a bunch of code to check for timestamp, type, currency,fee, desr as specific fields and formats
		# valid should be set as -1 i.e. not yet validated and block_index as <=0 so not yet included
		# specific_data format is dependent on type and hence needs to be coded for each type

	def mempoolpayment(self,sender,tokencode):
	#	if not mempool:
		mempool=self.mempool;
		filenames = os.listdir(mempool);
		mppayment=0;
		for filename in filenames:
			if "validation" in filename or ".json" not in filename:
				continue
			fl=mempool+filename;
		#	self.loadtransaction
			with open(fl,"r") as readfile:
				trandata=json.load(readfile)['transaction'];
			ttype=trandata['type'];
			if ttype<4:	#0 is genesis, 1 is wallet creation, 2 is token creation, 3 is token custody
				continue
			if ttype==5:	#unilateral transaction so will have only asset_1 number
				if sender==trandata['specific_data']['wallet1'] and trandata['specific_data']['asset1_code']==tokencode:
					mppayment+=trandata['specific_data']['asset1_number'];
			if ttype==4:	# bilateral trasnaction so will have both aset_1 and asset_2 numbers
				if sender==trandata['specific_data']['wallet1'] and trandata['specific_data']['asset1_code']==tokencode:
					mppayment+=trandata['specific_data']['asset1_number'];
				if sender==trandata['specific_data']['wallet2'] and trandata['specific_data']['asset2_code']==tokencode:
					mppayment+=trandata['specific_data']['asset2_number'];
		
		#	need to incorporate the fee as well in future
		return mppayment

	def econvalidator(self):
		# start with all holdings of the wallets involved and add validated transactions from mempool
		# from mempool only include transactions that reduce balance and not those that increase
		# check if the sender has enough balance to spend
		with open(self.statefile,"r") as statefl:
			try:
				state=json.load(statefl);
			except:
				"Couldn't load state file, either missing or invalid. Exiting"
				return False;
		self.validity=0
		if self.transaction['type']==1:
			custodian=self.transaction['specific_data']['custodian_wallet']
			custvalidity=False
			for wallet in state['all_wallets']:
				if wallet['wallet_address']==custodian:
					custvalidity=True
			if not custvalidity:
				print("No custodian address found")
			#	self.transaction['valid']=0
				self.validity=0
			else:
				print("Valid custodian address")
			#	self.transaction['valid']=1
				self.validity=1
			#additional check for allowed custodian addresses
				if os.path.exists("allowed_custodians.json"):
					print("Found allowed_custodians.json; checking against it.")
					custallowflag=False
					with open("allowed_custodians.json","r") as custfile:
						allowedcust=json.load(custfile)
					for cust in allowedcust:
						if custodian==cust['address']:
							print("Address ",custodian," is allowed as a custodian.")
							custallowflag=True
					if not custallowflag:
						print("Could not find address ",custodian," amongst allowed custodians.")
						self.validity=0

	#	self.validity=0
		if self.transaction['type']==2:		#token addition transaction
			firstowner=self.transaction['specific_data']['first_owner']
			custodian=self.transaction['specific_data']['custodian']
			fovalidity=False
			custvalidity=False
			for wallet in state['all_wallets']:
				if wallet['wallet_address']==firstowner:
					print("Valid first owner")
					fovalidity=True
				if wallet['wallet_address']==custodian:
					print("Valid custodian")
					custvalidity=True
			if not fovalidity:
				print("No first owner address found")
			#	self.transaction['valid']=0
				self.validity=0
			if not custvalidity:
				print("No custodian address found")
				self.validity=0
			if fovalidity and custvalidity:
				print("Valid first owner and custodian")
			#	self.transaction['valid']=1
				self.validity=1

	#	self.validity=0
		if self.transaction['type']==4 or self.transaction['type']==5:
			ttype=self.transaction['type'];
			startingbalance1=0;
			startingbalance2=0;
			sender1=self.transaction['specific_data']['wallet1']
			sender2=self.transaction['specific_data']['wallet2']
			tokencode1=self.transaction['specific_data']['asset1_code']
		#	tokencode2=self.transaction['specific_data']['asset2_code']
			#below, we include the starting balance as well as total payments in the mempool trnasactions
			token1mp=self.mempoolpayment(sender1,tokencode1);	#already includes the current transaction
		#	token2mp=self.mempoolpayment(sender2,tokencode2);	#already includes the current trasanction
			token1amt=max(self.transaction['specific_data']['asset1_number'],token1mp)
		#	token2amt=max(self.transaction['specific_data']['asset2_number'],token2mp)
			#the max above is required in case there is misspecification of mempool for any reason.
		#	token1amt=self.transaction['specific_data']['asset1_number']+self.mempoolpayment(sender1,tokencode1)
		#	token2amt=self.transaction['specific_data']['asset2_number']+self.mempoolpayment(sender2,tokencode2)
		#	with open(self.statefile,"r") as statefl:
		#		state=json.load(statefl);
			sender1valid=False
			sender2valid=False

			#for ttype=5, there is no tokencode for asset2 since it is off-chain, there is no amount either
			if ttype==4:	#some attributes of transaction apply only for bilateral transfer and not unilateral
			#	startingbalance2=0;
				tokencode2=self.transaction['specific_data']['asset2_code']
				token2mp=self.mempoolpayment(sender2,tokencode2);
				token2amt=max(self.transaction['specific_data']['asset2_number'],token2mp)
		
			#address validity applies to both senders in ttype 4 and 5; since sender2 is still receiving tokens
			for wallet in state['all_wallets']:
				if wallet['wallet_address']==sender1:
					sender1valid=True;
				if wallet['wallet_address']==sender2:
					sender2valid=True;
			if not sender1valid:
				print("Invalid sender1 wallet")
			#	self.transaction['valid']=0
				self.validity=0
			#	return False
			if not sender2valid:
				print("Invalid sender2 wallet")
			#	self.transaction['valid']=0
				self.validity=0
			#	return False

			#tokenvalidity applies for both senders only in ttype 4
			token1valid=False
		#	token2valid=True
			if ttype==4:
				token2valid=False	#by keeping it here, we ensure that no code refers to token2valid for type5
			for token in state['all_tokens']:
				if token['tokencode']==tokencode1:
					token1valid=True;
				if ttype==4:
					if token['tokencode']==tokencode2:
						token2valid=True;
			if not token1valid:
				print("Invalid asset1 code")
			#	self.transaction['valid']=0
				self.validity=0
			#	return False
			if ttype==4:
				if not token2valid:			
					print("Invalid asset1 code")
			#		self.transaction['valid']=0
					self.validity=0
			#		return False
			if ttype==4:
				if token1valid and token2valid:
					print("Valid tokens")
					self.validity=1
			else:	#this is ttype=5
				if token1valid:
					print("Valid tokens")
					self.validity=1
			
		#	if self.transaction['valid']==0:
			if self.validity==0:
				print("Transaction not valid due to invalid tokens or addresses")
				return False

			self.validity=0	# resetting to check the balances being sufficient, in futures, make different functions
			for balance in state['all_balances']:
				if balance['wallet_address']==sender1 and balance['tokencode']==tokencode1:
					startingbalance1=balance['balance']	#unique combination of sender and token
				if ttype==4:
					if balance['wallet_address']==sender2 and balance['tokencode']==tokencode2:
						startingbalance2=balance['balance']
			if token1amt > startingbalance1:	#sender1 is trying to send more than she owns
				print("sender1 is trying to send,",token1amt,"she owns,",startingbalance1," invalidating transaction")
			#	self.transaction['valid']=0;
				self.validity=0
			if ttype==4:
				if token2amt > startingbalance2:        #sender2 is trying to send more than she owns
					print("sender2 is trying to send more than she owns, invalidating transaction")
			#		self.transaction['valid']=0;
					self.validity=0
			if ttype==4:
				if token1amt <= startingbalance1 and token2amt <= startingbalance2: #double checking
					print("Valid economics of transaction. Changing economic validity value to 1")
				#	self.transaction['valid']=1;
					self.validity=1
			if ttype==5:
				if token1amt <= startingbalance1:
					print("Valid economics of transaction. Changing economic validity value to 1")
				#	self.transaction['valid']=1;
					self.validity=1

	#	if self.transaction['valid']==1:
		if self.validity==1:
			return True;
		else:
			return False;	# this includes the case where valid=-1 i.e. yet to be validated
		
#	def legalvalidator(self):
		# check the token restrictions on ownertype and check the type of the recipient


def main():
	tm=Transactionmanager()
#	walletdata=wm.wallet_maker()	
#this has the wallet data..like chain is to blockchain.. this is inert data. wm is an object
#	print(walletdata)
#	files=["currentstate.txt","policy.txt"]
#	kycdocs=[1,2]
#	wm.kycdocslinker(files,kycdocs)
#	wm.walletlistupdater()	#can do this without kyc docs or with them
#	wm.transactioncreator()
	print(tm.transaction)
#	filetest="data/mempool/transaction-1-2021-06-24-589621.json"
	filetest="data/mempool/transaction-1-2021-06-24-204748.json"
	tmnew=Transactionmanager()
	tmnew.loadtransactionpassive(filetest)
#	print(tmnew.transaction)
	tmnew.dumptransaction('filetest.json')
#	print(tm.econvalidator())
	keydata={"public": "STaLQEiLlNAvcLB6hSv3ItDPu3AAsgmZQKbsdAnK8ujA5CVzeGSSQZftzVEe+Tm0G+9ZKQUYjsK3AYYAqT7nWA==", "private": "BT8YI/4i4Uu3/3dCa2Pe04vho8NcChIjioSPhdVNIRo=", "address": "0x3762da843f54b08ef6401b9a5741600a16919c24"}
	keydata={"public": "wR7u4iF90Fh71Vy3QMRqxRQs7ygjVMFhGWC0F85vapHlronsbyCEyD7FQzpx02cwtI/dGyNBc/baIaDMuMyeHg==", "private": "SQYxlGwwr2Z2e40oAGPCnsPUthLKs6IFWCiloST8mPY=", "address": "0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42"}
	pvtkey=keydata["private"]		#this is in the form of base64 coded text, not binary string, not butes
	pvtkeybytes=base64.b64decode(pvtkey)	#this is in bytes
	print("pvtkeybytes:",pvtkeybytes)
	pubkey=keydata["public"]
	pubkeybytes=base64.b64decode(pubkey)
	address=keydata["address"]
#	address="0x3762da843f54b08ef6401b9a5741600a16919c24"
	signtransbytes=tm.signtransaction(pvtkeybytes,address)	#the sgining function now takes private keybytes
	signtrans=base64.b64encode(signtransbytes).decode('utf-8')	
	print("signtrans: ",signtrans)
	xx={'signtrans':signtrans}
	with open("xxx.json","w") as xfile:
		json.dump(xx,xfile)
	with open("xxx.json","r") as xfile:
		signtrans=json.load(xfile)['signtrans']

	print("single trans verification",tm.verifysign(signtrans,pubkeybytes,address))
	fullsigns=tm.verifytransigns()
	print("Full verification: ",fullsigns)
	print("public",pubkey,"\tprivate",pvtkey,)
	
#	wmnew.walletlistupdater()

#need to write more code to load a wallet and to update kyc docs etc

if __name__ == "__main__":
	main();


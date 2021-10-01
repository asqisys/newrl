# program to create and manage objects for wallets
import codecs
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import json
import datetime
from codes.transactionmanager import Transactionmanager
import base64

class Walletmanager:
	def __init__(self, walletfile="data/common/all_wallets.json"):
#		self.public=
		self.wallet={"address":None,
				"public":None,
				"private":None,
				"kyccustodian":None,
				"kycdocs":[],
				"dochashes":[],
				"ownertype":0,
				"jurisd":0,
				"specific_data":[]}
#		self.wallet['kycdocs']=[];
#		self.wallet['dochashes']=[];
#		self.wallet['ownertype']=0;	#integer 0=unknown, 1=individual, 2=artificial offchain entity
						# 3= artificial on-chain entity incl smart contracts
#		self.wallet['jurisd']=0;	# integer 0=unknown, 1=on-chain 2=India, 3=US,4=Singpore etc
#		self.wallet['specific_data']=[];	#list of numbers and strings, for artificial entities, empty for indvdls 
		self.walletrecords=walletfile;
		self.mempool="data/mempool/"

	def get_digest(self,file_path):
		h = hashlib.sha256()

		with open(file_path, 'rb') as file:
			while True:
            # Reading is buffered, so we can read smaller chunks.
				chunk = file.read(h.block_size)
				if not chunk:
					break
				h.update(chunk)
		return h.hexdigest()

#with open("data/common/chain.json", "rb") as read_file:
#file="./requirements.txt"
#print(get_digest(file))

	def createlinkedwallet(self):
		#this function creates a linked wallet that only has new address but all the attributes of current wallet
		newwallet=self.wallet;
#		self.wallet_maker(self,newwallet['kycdocs'],newwallet['dochashes'])
		newkeydata=self.address_maker();
		newwallet['public']=newkeydata['public']
		newwallet['private']=newkeydata['private']
		newwallet['address']=newkeydata['address']
#		newwallet['dochashes']=self.wallet['dochashes']
#		newwallet['kycdocs']=self.wallet['kycdocs']
		trans = self.transactioncreator(newwallet);
		trans.dumptransaction();
		return newwallet['address']

	def wallet_maker(self,kyccustodian=None,kycdocs=[],files=[],ownertype=0,jurisd=0,specific_data=[]):
		newkeydata=self.address_maker();
		self.wallet['public']=newkeydata['public']
		self.wallet['private']=newkeydata['private']
		self.wallet['address']=newkeydata['address']
		self.wallet['kyccustodian']=kyccustodian
		self.kycdocslinker(kycdocs,files);
		self.wallet['ownertype']=ownertype;
		self.wallet['jurisd']=jurisd;
		self.wallet['specific_data']=specific_data;
		print("Now adding transaction")
		trans = self.transactioncreator(self.wallet);
		transactionfile = trans.dumptransaction();
#		flname=self.mempool+"walletcreation-"+trans['timestamp'][0:9]+"-"+trans['timestamp'][-6:]+".json"
#		with open(flname,"w") as writefile:
#			json.dump(trans, writefile);
#			print("Wrote to ",flname)
		keysdata=[{'address':self.wallet['address'],'public':self.wallet['public'],'private':self.wallet['private']}]
	#	return self.wallet['address']
		# return keysdata 	#to be used in wallet-file creation
		return transactionfile, keysdata

	def address_maker(self):
		private_key_bytes = os.urandom(32)
		keydata={'public':None,'private':None,'address':None}
		key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key

		key_bytes = key.to_string()
		private_key = codecs.encode(private_key_bytes, 'hex')
		public_key = codecs.encode(key_bytes, 'hex')

#		print("Private key: ",private_key)
#		print("Public key: ",public_key)
#		self.wallet['public']=public_key
#		self.wallet['private']=private_key
#		keydata['public']=public_key
#		keydata['private']=private_key

		public_key_bytes = codecs.decode(public_key, 'hex')

		hash = keccak.new(digest_bits=256)
		hash.update(public_key_bytes)
		keccak_digest = hash.hexdigest()

		address = '0x' + keccak_digest[-40:]
		print("Address:",address)
#		self.wallet['address']=address
		keydata['address']=address

		#the below section is to enable serialization while passing the keys through json 
		private_key_final=base64.b64encode(private_key_bytes).decode('utf-8')
		public_key_final=base64.b64encode(key_bytes).decode('utf-8')
		keydata['private']=private_key_final
		keydata['public']=public_key_final

#		self.wallet['kycdocs'].append();
		return keydata

#	data=[{"public":"b'b4a3953cbbb81edc4fd8cb35cfa11bf3950c2ef4c8ecd69297e7356b28e4f4d18b4a9448591db91af08849dbbb3664db1b8e7d1bf8522d339da64e19ab31c3e1'","private":"b'57404092b4b1f7393f60dd2d926dc0e38510944cb90266a56c1bac0580c2a9a3'","address":"0x0840a0cb6dd67d9ef1e8dc572095d21c970982f7"}]

	def walletlistupdater(self,publicflag=False):
	# probably a redundant function for now, all new wallets are updated from the wallet maker
#		if not os.path.exists(allwalletfile):
#			with open("data/common/all_wallets.json", 'w') as file:
#				json.dump(data, file)

		# this currently follows the convention that if the address is present, the updation of kyc cannot be done;
		# kyc has be to linked at the time of new wallet creation itself, if added later, it needs to be with a new wallet
		wallet=self.wallet
		public_key=wallet['public']
		if publicflag:	#the private key will not be recorded
			private_key="000000"
		else:
			private_key=wallet['private']	#private key will be recorded in this case
		address=wallet['address']
		kyccustodian=wallet['kyccustodian']
		kycdocs=wallet['kycdocs']
		dochashes=wallet['dochashes']
		ownertype=wallet['ownertype']
		specific_data=wallet['specific_data']
		jurisd=wallet['jurisd']
		allwalletfile=self.walletrecords
		with open(allwalletfile, 'r+') as file:
#	with open("data/common/chain.json",'r') as file:
			data=json.load(file)
#			print(data)
			keysaddress={"public":str(public_key), 
					"private":str(private_key), 
					"address":str(address),
					"kyccustodian":kyccustodian,
					"kycdocs":kycdocs,
					"dochashes":dochashes,
					"ownertype":ownertype,
					"jurisd":jurisd,
					"specific_data":specific_data}
#		file.write(str(keysaddress))
#			for walletdata in data:
#				if walletdata['public']==wallet['public']:
#					print("Public key already present in all_wallets, not updating")
#					return 
			if self.iswalletlisted():
				print("Public key already present in all_wallets, not updating")
				return False
			else:
				print("New wallet address; adding to records in ",allwalletfile)
				data.append(keysaddress)
				file.seek(0)
				json.dump(data, file)
				return True
#		json.dump(keysaddress,file)

	def iswalletlisted(self):
		allwalletfile=self.walletrecords
		with open(allwalletfile, 'r') as file:
			data=json.load(file)
			for walletdata in data:
#				print("datainfile: ",walletdata['address'],"\tdataloaded: ",self.wallet['address'])
				if walletdata['address']==self.wallet['address']:
#					print("Found a match!")
					return True
					break
		return False
		
	def dochasher(self, files):
#		files=["./requirements.txt","./currentstate.txt"]
		filehashes=[]
		for file in files:
			flhash = self.get_digest(file)
			filehashes.append(flhash)
		return filehashes;


	def kycdocslinker(self,kycdocs,files):
#		filehashes=[]
#		wallet=self.wallet
		for file in files:
			if not file:
				continue
			flhash = self.get_digest(file)
#			filehashes.append(flhash)
			self.wallet['dochashes'].append(flhash)
		for kycdoc in kycdocs:
			self.wallet['kycdocs'].append(kycdoc)

	def transactioncreator(self,wallet=None):
		if not wallet:
			wallet=self.wallet
		address = wallet['address']
		public = wallet['public']
		timestamp = str(datetime.datetime.now());
		text = "New wallet"
		kyccustodian=wallet['kyccustodian']
		kyc_docs = wallet['kycdocs']
		kyc_doc_hashes=wallet['dochashes']
		ownertype=wallet['ownertype']
		jurisd=wallet['jurisd']
		specific_data_wallet=wallet['specific_data'];
		valid = True
		transaction = {'timestamp': timestamp, 
				'type': 1, 
				'currency':"INR", 
				'fee':0.0 , 
				'descr':text,
				'valid':-1, 
			#	'block_index': 0,
				'specific_data':{'custodian_wallet':kyccustodian,
						'kyc_docs':kyc_docs,
						'kyc_doc_hashes':kyc_doc_hashes,
						'ownertype':ownertype,
						'wallet_address':address,
						'wallet_public':public,
						'jurisd':jurisd,
						'specific_data':specific_data_wallet}
				}
	#	print(transaction)
		signatures=[]
		transactiondata={'transaction':transaction,'signatures':signatures}
		trans=Transactionmanager();
		trans.transactioncreator(transactiondata);
		return trans

	def loadwallet(self, walletdata):
#		self.wallet={"address":"0000","public":"00000","private":"000000","kycdocs":[],"dochashes":[]}	
		try:
			self.wallet['public']=walletdata['public']
			self.wallet['private']=walletdata['private']
			self.wallet['address']=walletdata['address']
			self.wallet['kyccustodian']=walletdata['kyccustodian']
			self.wallet['kycdocs']=walletdata['kycdocs']
			self.wallet['dochashes']=walletdata['dochashes'];
			self.wallet['ownertype']=walletdata['ownertype'];
			self.wallet['jurisd']=walletdata['jurisd'];
			self.wallet['specific_data']=walletdata['specific_data'];
			return self.wallet
		except:
			print("Invalid wallet format")
			return False

def main():
	print("This is not a regular program to run, it's a common file")

#need to write more code to load a wallet and to update kyc docs etc

if __name__ == "__main__":
	main();


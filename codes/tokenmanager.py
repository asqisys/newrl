# Python programm to create object that enables addition of a block

import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from codes.blockchain import Blockchain
from codes.transactionmanager import Transactionmanager

class Tokenmanager():

	def __init__(self, tokenfile=None):
		self.tokenrecordsfile="all_tokens.json";
		if tokenfile:
			self.tokendata=self.loadtoken(tokenfile);
			print("Loaded token from ",tokenfile)
		else:
			self.tokendata={"tokencode":0,
				"tokenname":None,
				"tokentype":0,
				"tokenattributes":{},
				"first_owner":None,
				"custodian":None,
				"legaldochash":None,
				"amount_created":0,
				"value_created":0,
				"disallowed":[],
				"sc_flag":False}
	
	def load_attributes(self,attfile):
	# this is expected to be useful in case one wants to specify token attributes in a separate file from token data
		with open(tokenfile,"r") as readfile:
			attributes=json.load(readfile);
			try:
				self.tokendata['tokenattributes']=attributes;
				return True
			except:
				print("Invalid file format")
				return False			

	def dumptokendata(self,tokenfile):
	#this just dumps token data without checking about its validity or being present in records
		with open(tokenfile,"w") as writefile:
			try:
				json.dump(self.tokendata,writefile)
			except:
				print("Couldn't dump data, probably wrong format")
		
	def loadtoken(self,tokenfile):
	#this function just loads a token from a file; may be valid or invalid, maybe in the records or not.
		with open(tokenfile,"r") as readfile:
			print("Now reading from ",tokenfile)
			tokendata=json.load(readfile);	
			try:
				self.tokendata=tokendata;
			#	return True
			except:
				print("Invalid file format")
				return False

	def loadandcreate(self,tokenfile,mempool,statefile):
	#this function loads presumably new token attributes from a file, with an intent to create a new token
	#it ignore token code if any, increments it by 1 from tokenreocrds file and re-writes the tokenfile as well
		self.loadtoken(tokenfile);
		tokenrecordsfile=self.tokenrecordsfile;
		if self.istokeninrecords():
			print("Either token already in record or token code reused. Set tokencode in file to 0 and try again if trying to add a new token. Else ignore")
			return False
		else:
			maxtcode=self.maxtokencode()
			self.tokendata["tokencode"]=maxtcode+1;
			self.create_token()	
			with open(tokenfile,"w") as writefile:
				json.dump(self.tokendata,writefile)	#writing back with updated tokencode to the tokefile
			#now adidng transaction
			transaction={'timestamp':str(datetime.datetime.now()),
			#	'trans_code':"000000"
				'type':2,
				'currency':"INR",
				'fee':0.0 ,
				'descr':"New token creation",
				'valid':1,
				'block_index': 0,
				'specific_data':self.tokendata}			
			trans=Transactionmanager(mempool, statefile);
			signatures=[]
			transactiondata={'transaction':transaction,'signatures':signatures}
			trans.transactioncreator(transactiondata);
			trans.dumptransaction();

	def sccreate(self,tokendata):
	#this function loads data from a contract call, with an intent to create a new token
	#it ignore token code if any, increments it by 1 from tokenreocrds file and re-writes the tokenfile as well
		self.tokendata=tokendata;
		tokenrecordsfile=self.tokenrecordsfile;
		if self.istokeninrecords():
			print("Either token already in record or token code reused. Set tokencode in file to 0 and try again if trying to add a new token. Else ignore")
			return False
		else:
			maxtcode=self.maxtokencode()
			self.tokendata["tokencode"]=maxtcode+1;
			self.create_token()
			transaction={'timestamp':str(datetime.datetime.now()),
			#	'trans_code':"000000"
				'type':2,
				'currency':"INR",
				'fee':0.0 ,
				'descr':"New token creation",
				'valid':1,
				'block_index': 0,
				'specific_data':self.tokendata}			
			trans=Transactionmanager(mempool, statefile);
			signatures=[]
			transactiondata={'transaction':transaction,'signatures':signatures}
			transaction_all=trans.transactioncreator(transactiondata);
			return transaction_all;

	def istokeninrecords(self):
		tokenrecordsfile=self.tokenrecordsfile;
		with open(tokenrecordsfile,"r+") as tokenrecords:
			tokenrecs=json.load(tokenrecords);
			for tokenrec in tokenrecs:
				if tokenrec["tokencode"]==self.tokendata["tokencode"]:
					return True
		return False

	def maxtokencode(self):
		tokenrecordsfile=self.tokenrecordsfile;
		maxtokencode=0;
		with open(tokenrecordsfile,"r+") as tokenrecords:
			tokenrecs=json.load(tokenrecords);
			for tokenrec in tokenrecs:
				if tokenrec["tokencode"]>maxtokencode:
					maxtokencode= tokenrec["tokencode"];
		return maxtokencode;

	def create_token(self):
		#do not use this for creating a new token; this only adds new token to records; use loadandcreate instead
		tokenrecordsfile=self.tokenrecordsfile;
		with open(tokenrecordsfile,"r+") as tokenrecords:
			tokenrecs=json.load(tokenrecords);
			newrecord=self.tokendata;
#			for tokenrec in tokenrecs
			print("Adding new token in ",tokenrecordsfile)
			try:
				tokenrecs.append(newrecord)
				tokenrecords.seek(0)
				json.dump(tokenrecs, tokenrecords)
				print("Successfully added new token to ",tokenrecordsfile)
				return True
			except:
				print("Couldn't add new token.")
				return False

def main():
	parser = OptionParser();
	parser.add_option("-t", "--tokenfile", dest="tokenfile",default="tokennew.json",help="Input tokenfile. default - tokennew.json");
	(options, args) = parser.parse_args()
	newtoken=Tokenmanager()
	print(newtoken.tokendata)
	print(newtoken.istokeninrecords())
	newtoken.dumptokendata("tdump1.json")
	newtoken.loadandcreate(options.tokenfile)
	newtoken.dumptokendata("tdump2.json")
#	cs=chainscanner(options.tokenfile)
#	print(cs.chainlength)
#	print(cs.gettransactions(3))

if __name__ == "__main__":
	main();


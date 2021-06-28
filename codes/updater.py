# Python programm to create object that enables addition of a block

import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser

from blockchain import Blockchain
from transactionmanager import Transactionmanager
from chainscanner import Chainscanner

def chainmatch(chain1, chain2):
	len1=len(chain1)
	len2=len(chain2)
	commonlen=min(len1,len2)
	index=1;
	while index<commonlen+1:
		blockdata1=chain1[index-1]
		blockdata2=chain2[index-1]
		index+=1
		if not blockdata1['previous_hash']==blockdata2['previous_hash']:
			return False
		if not blockdata1['proof']==blockdata2['proof']:
			return False
	return True

def main():

	parser = OptionParser()
	parser.add_option("-c", "--chainfile", dest="chainfile",default="chain.json",help="Input chainfile. default - chain.json");
	parser.add_option("-m", "--mempool", dest="mempool",default="./mempool/",help="Mempool directory. default - ./mempool/");
	parser.add_option("-i", "--itpool", dest="itpool",default="./incltranspool/",help="Included transactions directory. default - ./incltranspool/");	
	parser.add_option("-s", "--state", dest="state",default="state.json",help="Statefile. default - state.json");

	(options, args) = parser.parse_args()
	globaldir="/data/asqi/newrl/"
	#blockchain = Blockchain("inginesis.json")
	blockchain = Blockchain(options.chainfile)
	statefile=options.state
	cs_prev=Chainscanner(options.chainfile)
#	blockchain = Blockchain();
#	blockchain.loadfromfile("chain.json");
	
	destchain=globaldir+options.chainfile
	deststate=globaldir+options.state
	if os.path.exists(destchain):
		print("Found global chain. Checking for match with local.")
		globalchain=Blockchain(destchain)
		if globalchain.chain_valid(globalchain.chain):
			if chainmatch(globalchain.chain,blockchain.chain):
				print("Global chain matching local chain available, checking for update.")
				if len(globalchain.chain)<=len(blockchain.chain):
					print("Chains are of matching and local chain is longer or of same length, not updating local.")
				else:
					print("Chains are of matching but global longer than local, updating local file and loading it again.")
					shutil.copy(destchain,options.chainfile)
					blockchain = Blockchain(options.chainfile)
			else:
				print("Global chain does not match local chain. Investigae. Not copying to local but continuing with local-only update.")
		else:
			print("Global chain is not valid, investigate. Continuing with local-only update.")
	else:
		print("No global chain found. Continuing with local-only update.")
		
	max_block_height = 10;
	block_time_limit = 1;	#number of hours of no transactions still prompting new block
	block_height = 0;
	latest_ts = blockchain.get_latest_ts(); 

	mempool = options.mempool
	incltrans = options.itpool
	filenames = os.listdir(mempool);	#this is the mempool
	print("Files in mempool: ",filenames)
	textarray=[];
	signarray=[];
	transfiles=[]
	validationfiles=[]
	tmtemp=Transactionmanager(options.mempool,options.state)
	for filename in filenames:
		if "validation" in filename:        #the validation files
			validationfiles.append(filename)
		if "transaction" in filename:
			transfiles.append(filename)

	for filename in transfiles:
		file=mempool+filename;
	#	if "validation" in file:	#the validation files
	#		continue
		if ".json" in file:
			try:
				with open(file, "r") as read_file:
					print("processing ",file)
					transactiondata=json.load(read_file)
			except:
				print("Couldn't load transaction file ",file)
				continue	
			transaction=transactiondata['transaction']
			signatures=transactiondata['signatures']
#			print(transaction)
			ts = datetime.datetime.strptime(transaction["timestamp"][:-7],"%Y-%m-%d %H:%M:%S");
#			print(ts)
#			if ts > latest_ts:
#				print("Found transaction after latest_ts with ts = ",ts)
	#			print(transaction['valid'])

			#new code for validating again
			trandata=tmtemp.loadtransactionpassive(file);
			if not tmtemp.verifytransigns():
				print("Transaction id ",trandata['transaction']['trans_code']," has invalid signatures")
				continue
			if not tmtemp.econvalidator():
				print("Economic validation failed for transaction ", trandata['transaction']['trans_code'])
				continue
			# end new code
			trancodestr=trandata['transaction']['trans_code']
			totalchecks=0
			validchecks=0
			specificvalfiles=[]
			for flname in validationfiles:
				if trancodestr in flname:
					validationfile=mempool+flname
					specificvalfiles.append(validationfile)	#to enable easy move out later from mempool
					try:
						with open(validationfile,"r") as read_file:
							validitydata=json.load(read_file)
						totalchecks+=1	#all checks including those that rejected
						if validitydata['valid']==1:
							validchecks+=1	# only the successful checks
					except:
						print("could not load validity data from ",validationfile)
			tranvalidity=0
			if totalchecks<1:
				tranvalidity=0
			else:
				print("Proportion of valid checks = ",float(validchecks/totalchecks))
				if float(validchecks/totalchecks)>0.5:	#majority
					tranvalidity=1
		#	if transaction['valid']==1:
			traninclusionflag=False
			if tranvalidity==1:
			#	print("Found valid transaction, adding to block. Moving file to ",incltrans)
				print("Found valid transaction, checking if it is already included")
				alltranids=cs_prev.getalltransids()
				for tranid in alltranids:
					if tranid['trans_code']==transaction['trans_code']:
						print("Transaction with id ",transaction['trans_code']," is already included in block number ",tranid['blockindex'])
						traninclusionflag=True
						break
				if traninclusionflag:	#the current transaction is already included in some earlier block
					continue	#this takes the process to the next transaction	

				textarray.append(transaction);
				signarray.append(signatures);
				try:
					shutil.move(file, incltrans);
				except:
					print("Couldn't move,",file);
				for vfile in specificvalfiles:
					try:
						shutil.move(vfile, options.itpool)
					except:
						print("couldn't move ",vfile)
				block_height+=1;
				if block_height>=max_block_height:
					print("Reached max block height, moving forward with the collected transactions")
					break;
			else:
				print("Did not find valid transaction, not adding to block")
#			else:
#				print("Transaction before the latest timestamp; not adding to block")

	transactionsdata={"transactions":textarray,"signatures":signarray}
	if len(textarray)>0:
#		transactions={"transactions":textarray}
		print("Found some transactions; adidng to chain")
	else:
		print("No new transactions,checking for time.")
		print("latest ts:",latest_ts,"\tNow: ",datetime.datetime.now())
		print("Time since last block: ",round((datetime.datetime.now() - latest_ts).total_seconds()/3600,2), " hours")
		if (datetime.datetime.now() - latest_ts).total_seconds() < 3600*block_time_limit:     #no transactions for 1 hours
			print("No new transactions, not enough time since last block. Exiting.")
			exit();
		else:
			print("More than ",block_time_limit," hours since the last block, adding a new empty one")

	blockchain.mine_block(transactionsdata);

	if blockchain.chain_valid(blockchain.chain):
#		chainjsonstr=json.dumps(blockchain.chain);
		with open(options.chainfile,"w") as chainwrite:
			json.dump(blockchain.chain, chainwrite);
		print("Wrote to ",options.chainfile);
		#updating state now
		cs=Chainscanner(options.chainfile)
		all_wallets=cs.getallwallets()
		all_tokens=cs.getalltokens()
		all_balances=cs.getallbalances()
		newstate={'all_wallets':all_wallets,'all_tokens':all_tokens,'all_balances':all_balances}
		if os.path.exists(options.state):
			ts=str(datetime.datetime.now());
			statearchivefile='./statearchive/statefile_'+ts[0:10]+"-"+ts[-6:]+".json"
			shutil.copy(options.state,statearchivefile)
			print("Copied existing state file - ",options.state," - to ",statearchivefile)
		with open(options.state,'w') as writefile:
			json.dump(newstate,writefile)
			print("Wrote new state to ",options.state)	
		
		print("Local chain updated. Now attempting to update global chain.")
		destchain=globaldir+options.chainfile
		deststate=globaldir+options.state
		if os.path.exists(destchain):
			print("Found global chain to update")
			try:
				with open(destchain,"r") as gcfile:
					globalchain=json.load(gcfile)
				print("Loaded globalchain")
			except:
				print("Could not load globalchain. Exiting without updating global. Investigate.")
				globalchain=[]
				return True
		
			if not chainmatch(globalchain,blockchain.chain):	#globalchain exists but does not match, exit
				print("Common portion of global and local chains do not match. Not updating global chain.")
				return True	#important to exit to avoid copying local to global
		try:
			shutil.copy(options.chainfile,destchain)	#if globalchain does not exist, this will create it
			print("Updated global chain with local copy.")
			os.chmod(destchain,0o666)
			print("Changed mode to 666")
		except:
			print("Couldn't upload global chain or change its mode to 666, investigate.")
		try:
			shutil.copy(options.state,deststate)
			print("Updated global state with local copy.")
			os.chmod(deststate,0o666)
			print("Changed mode to 666")
		except:
			print("Couldn't update global state or change its mode to 666, investigate.")

	else:
		print("Invalid blockchain, not changing anything.")
		
#	print(blockchain.chain)
#	print(blockchain.get_latest_ts())

if __name__ == "__main__":
	main();


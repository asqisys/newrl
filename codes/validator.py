# Python programm to validate trnasctions starting with data/common/state.json and mempool

#in current version, it edits the transaction file or at least creates a new version of it post validation.. this works for permissioned variatn.. later, for decentralize dversion, we will need to alter the file altering with new validation receipt creation..

import datetime
import hashlib
import json
import os
import shutil
from optparse import OptionParser
from codes.chainscanner import Chainscanner
from codes.blockchain import Blockchain
from codes.transactionmanager import Transactionmanager

def econvalidator(mempool="data/mempool/"):
#	print("hellooooo babies!")
	filenames = os.listdir(mempool);
	tm1=Transactionmanager()	
	for filename in filenames:
		file=mempool+filename;
		tm1.loadtransaction(file)
		if not tm1.econvalidator():
			continue;
		else:
			print("Hello")			
	#	with open(file, "r") as read_file:
			


def main():

	parser = OptionParser()
	parser.add_option("-t", "--transfile", dest="transfile",default=None,help="Input transactionfile. default - None");
	parser.add_option("-s", "--state", dest="state",default="data/common/state.json",help="Statefile. default - data/common/state.json");
	parser.add_option("-m", "--mempool", dest="mempool",default="data/mempool/",help="mempool directory. default - data/mempool/");	
	(options, args) = parser.parse_args()
	#blockchain = Blockchain("inginesis.json")
#	blockchain = Blockchain(options.chainfile)
#	blockchain = Blockchain();
#	blockchain.loadfromfile("data/common/chain.json");

	ts=str(datetime.datetime.now());
	tm=Transactionmanager(options.mempool, options.state)
	tm.loadtransactionpassive(options.transfile)
	econ=tm.econvalidator()
	signvalid=tm.verifytransigns()
	valid=0
	if econ and signvalid:
#		tm.dumptransaction(options.transfile);
		msg="All well"
		valid=1
	if not econ:
		msg="Economic validation failed"
	if not signvalid:
		msg="Invalid signatures"
	check={'valid':valid,'msg':msg}
	
	checkfile=options.mempool+tm.transaction['trans_code']+"_validation"+str("-"+ts[0:10]+"-"+ts[-6:]+".json")
	with open(checkfile,"w") as ckfile:
		json.dump(check,ckfile)
	print("Wrote check status as ",check,"to ",checkfile)	
#	econvalidator();
#	cs=Chainscanner(options.chainfile)
#	all_wallets=cs.getallwallets()
#	all_tokens=cs.getalltokens()
#	all_balances=cs.getallbalances()
#	newstate={'all_wallets':all_wallets,'all_tokens':all_tokens,'all_balances':all_balances}
	
#	if os.path.exists(options.state):
#		statearchivefile='data/statearchive/statefile_'+str(self.transaction['type'])+"-"+ts[0:10]+"-"+ts[-6:]+".json"
#		shutil.copystat(options.state,statearchivefile)
#		print("Copied existing state file - ",options.state," - to ",statearchivefile)
#	with open(options.state,'w') as writefile:
#		json.dump(newstate,writefile)
#		print("Wrote new state to ",options.state)		

if __name__ == "__main__":
	main();



def validate(transfile, mempool="data/mempool/", state="data/common/state.json"):
	#blockchain = Blockchain("inginesis.json")
#	blockchain = Blockchain(options.chainfile)
#	blockchain = Blockchain();
#	blockchain.loadfromfile("data/common/chain.json");

	ts=str(datetime.datetime.now());
	tm=Transactionmanager(mempool, state)
	tm.loadtransactionpassive(transfile)
	econ=tm.econvalidator()
	signvalid=tm.verifytransigns()
	valid=0
	if econ and signvalid:
#		tm.dumptransaction(options.transfile);
		msg="All well"
		valid=1
	if not econ:
		msg="Economic validation failed"
	if not signvalid:
		msg="Invalid signatures"
	check={'valid':valid,'msg':msg}
	
	checkfile=mempool+tm.transaction['trans_code']+"_validation"+str("-"+ts[0:10]+"-"+ts[-6:]+".json")
	with open(checkfile,"w") as ckfile:
		json.dump(check,ckfile)
	
	if valid==1:	#econ and signvalid are both True
		transoutputfile=mempool + "transaction-" + str(tm.transaction['type']) + "-" + tm.transaction['trans_code'] + ".json"
		tm.dumptransaction(transoutputfile);
	
	status = f"Wrote check status as {check} to {checkfile}"
	print(status)	
	return status

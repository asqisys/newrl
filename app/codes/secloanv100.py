# class to create smart contract for loan with bullet repayment
import codecs
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import json
import datetime
import time
import binascii
import base64
import sqlite3

from .transactionmanager import Transactionmanager
from .chainscanner import Chainscanner, get_wallet_token_balance
from .tokenmanager import create_token_transaction

class SecLoan1():
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class
    def __init__(self,contractaddress=None):
        self.template="secloan1"
        self.version="1.0.0"
        self.address=contractaddress    #this is for instances of this class created for tx creation and other non-chain work
        if contractaddress:     #as in this is an existing contract
            self.loadcontract(contractaddress)  #this will populate the params for a given instance of the contract
        #instantiation convetion: for the first time instantiation of a contract, the contractaddress is None, this is to be immediately followed by setup call
        #in a later call outside chain work or inside it, the contractaddress is present and is used to lookup the specific contract from the db

    def setup(self,callparamsjson):
        #this is called by a tx type 3 signed by the creator, it calls the function setp with parameters as params
        #setup implies a transaction for contract address creation
        callparams=json.loads(callparamsjson)
        contractparams=callparams
        if contractparams['status']==-1:
            print("Contract is already terminated, cannot setup. Exiting.")
            return False
        if contractparams['status']==2:
            print("Contract already deployed, cannot setup. Exiting.")
            return False
        if contractparams['status']==3:
            print("Contract already expired, cannot setup. Exiting.")
            return False
        if contractparams['status']==1:
            print("Contract already setup, cannot setup again. Exiting.")
            return False
        #add other codes here if in future 4 onwards are used for specifying other contract states.
        
        private_key_bytes = os.urandom(32)
        key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
        key_bytes = key.to_string()
        public_key = codecs.encode(key_bytes, 'hex')
        public_key_bytes = codecs.decode(public_key, 'hex')
        hash = keccak.new(digest_bits=256)
        hash.update(public_key_bytes)
        keccak_digest = hash.hexdigest()
        self.address = '0x' + keccak_digest[-40:]   # this overwrites the None value in the init call, whenever on-chain contract is setup
        # we have ignored the private key and public key of this because we do not want to transact through key-based signing for a contract

        # next we set up the contract status as live
        # params={}
        if contractparams['name']!=self.template:
            print("Mismatch in contractname. Not creating a new contract.")
            return False
        if contractparams['version']!=self.version:
            print("Mismatch in contract version. Not creating a new contract.")
            return False
        contractparams['status']=1
        #status convention: 0 or None is not setup yet, 1 is setup but not deployed, 2 is setup and deployed, 3 is expired and -1 is terminated
        
        # now we need to update the contract parameters in SC database; for now we are appending to the allcontracts.json
        contractparams['ts_init'] = time.mktime(datetime.datetime.now().timetuple())
        #contractparams['ts_init']=str(datetime.datetime.now()
        contractparams['address']= self.address
        self.contractparams=contractparams
        #########
        #code to append contractdata into allcontracts db
        sdestr=0 if not contractparams['selfdestruct'] else int(contractparams['selfdestruct'])
        cstatus = 0 if not contractparams['status'] else int(contractparams['status'])
        cspecs=json.dumps(contractparams['contractspecs'])
        legpars=json.dumps(contractparams['legalparams'])
        qparams=(self.address,
                contractparams['creator'],
                contractparams['ts_init'],
                contractparams['name'],
                contractparams['version'],
                contractparams['actmode'],
                cstatus,
                contractparams['next_act_ts'],
                contractparams['signatories'],
                contractparams['parent'],
                contractparams['oracleids'],
                sdestr,
                cspecs,
                legpars
                )
        con = sqlite3.connect('newrl.db')
        cur = con.cursor()
        cur.execute(f'''INSERT INTO contracts
                (address, creator, ts_init, name, version, actmode, status, next_act_ts, signatories, parent, oracleids, selfdestruct, contractspecs, legalparams)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', qparams)
        con.commit()
        con.close()
        #########
        return self.address

    def loadcontract(self,contractaddress):
        #this loads the contract from the state db
        #it should take as input contractaddress and output the contractparams as they are in the db as of the time of calling it
        #the output will populate self.contractparams to be used by other functions
        con = sqlite3.connect('newrl.db')
        cur = con.cursor()
        contract_cursor = cur.execute('SELECT * FROM contracts WHERE address = :address', {
                    'address': contractaddress})
        contract_row = contract_cursor.fetchone()
        contract = contract_row if contract_row is not None else 0
        con.close()
        #print(contract)
        self.contractparams={}
        self.contractparams['address']=contractaddress
        self.contractparams['creator']=contract[1]
        self.contractparams['ts_init']=contract[2]
        self.contractparams['name']=contract[3]
        self.contractparams['version']=contract[4]
        self.contractparams['actmode']=contract[5]
        self.contractparams['status']=contract[6]
        self.contractparams['next_act_ts']=contract[7]
        self.contractparams['signatories']=contract[8]
        self.contractparams['parent']=contract[9]
        self.contractparams['oracleids']=contract[10]
        self.contractparams['selfdestruct']=contract[11]
        self.contractparams['contractspecs']=contract[12]
        self.contractparams['legalparams']=contract[13]
        print("Loaded the contract with following data: \n",self.contractparams)
        return self.contractparams

    #the below function creates the transaction of a give type
    def create_tx(self,ttype,tspdata,currency="INR",fee=0.0,mempool="./mempool",statefile="./state.json",descr=None): 
        transaction={'timestamp':str(datetime.datetime.now()),
                    'type':ttype,
                    'currency':currency,
		            'fee':fee,
                    'descr':descr,
                    'valid':1,
                    'block_index':0,
                    'specific_data':tspdata}
        # the below section is to be re-written upon the database version conclusion
        trans=Transactionmanager(mempool, statefile);
        signatures=[]
        transactiondata={'transaction':transaction,'signatures':signatures}
        txdata=trans.transactioncreator(transactiondata);
        #trans.dumptransaction(txfilename);  #the tx is created at the location txfilename, to uncomment this, add txfilename to the arguments above
        return txdata   #this is expected to be used in API form, hence the caller gets back the tx data as a json object

    def create_sc_tx(self,function,params):
        specificdata={'template':self.template,
                      'version':self.version,
                      'function':function,
                      'params': params}
        tx=self.create_tx(3,specificdata,"INR",0.0) #going with default values for mempool="./mempool",statefile="./state.json",descr=None
        return tx        
        # user will take this transaction and submit its signed version for inclusion in a block,
        # validators will simply check if it is signed properly and for fees; maybe also for technical accuracy of params being suitable for template

    def create_child_txs(self):
        #this is not a chain process, it is called by user/front end app to generate tx to be signed by individual parties
        loantokentx=self.create_loan_token();
        lendtransfertx=self.transferlend();
        sectransfertx=self.transfersec();
        return loantokentx,lendtransfertx,sectransfertx;    #calling api will get three json objects
        
    def getcontaddbal(self,chainfile="./chain.json"):
        cs=Chainscanner(chainfile)
        contloanbal=cs.getbaladdtoken(self.contractaddress,self.contractparams['contractspecs']['loantokencode'])
        conttokbal=cs.getbaladdtoken(self.contractaddress,self.contractparams['contractspecs']['tokencode'])
        contsecbal=cs.getbaladdtoken(self.contractaddress,self.contractparams['contractspecs']['sec_token_code'])
        return{"contloanbal":contloanbal,"conttokbal":conttokbal,"contsecbal":contsecbal}

    def deploy(self,callparams):
        # carries out the loan execution steps upon instruction from a transaction - during updater run, post block inclusion
        if self.contractparams['status'] != 1:    #the contract is not setup, i.e. is either yet to be setup, already deployed or terminated
            print("The contract is not in the post-setup stage. Exiting without deploying.")
            return False
        contbalances=self.getcontaddbal();
        contloanbal=contbalances['contloanbal']
        conttokbal=contbalances['conttokbal']
        contsecbal=contbalances['contsecbal']
        if contloanbal>= self.contractparams['contractspecs']['loanamount'] and conttokbal >= self.contractparams['contractspecs']['loanamount'] and contsecbal >=self.contractparams['contractspecs']['sec_token_amount']:
            #########
            #code for deployment
            # 1. code to open the balances db and transfer lent tokens from contract to borrower, and loan tokens from contract to lender
            # 2. set up the activation date as the start date + tenor (given this is a bullet repayment loan) if type if hybrid or time-based
            # change status to deployed
            self.contractparams['status']=2     # changed from 1 (setup done) to 2 (deployed and live)
            self.contractparams['next_act_ts'] = self.contractparams['contractspecs']['due_date']   #this is so only for bullet repayment, else this will be emi date
            #update the status in the db as well
            #########
            print("Deployed smart contract - ",self.template,"with address ",self.contractaddress)
            return True
                
        else:
            print("One of the pre-conditions yet to be fulfilled, not deploying.")
            return False

    def create_loan_token(self):
        name="Secloantoken"+self.address[:5]
        contractspecs=json.loads(self.contractparams['contractspecs'])
        tokendata={"tokencode": 0,
                   "tokenname": name,
                   "tokentype": 62,
                   "tokenattributes": self.contractparams,
                   "first_owner": self.address,   #first owner is contract address till the contract is executed
                   "custodian": contractspecs['borrowerwallet'],
                   "legaldochash": self.contractparams['legalparams'],
                   "amount_created": contractspecs['loanamount'],
                   "value_created": contractspecs['loanamount'],
                   "disallowed": [],
                   "sc_flag": True,
                   "sc_address": self.address}
        tx=create_token_transaction(token_data=tokendata);
        #tx = loantoken.sccreate(tokendata);
        #self.contractparams['contractspecs']['loantokencode'] = tx['transaction']['specific_data']['tokencode']
        print(tx)
        return tx

    def transferlend(self):
        transferdata={"asset1_code": self.contractparams['contractspecs']['tokencode'],
                        "asset2_code": 0,
                        "wallet1": self.contractparams['contractspecs']['lenderwallet'],
                        "wallet2": self.contractaddress,
                        "asset1_number": self.contractparams['contractspecs']['loanamount'],
                        "asset2_number": 0}
        tx=self.create_tx(5,transferdata,"INR",0.0) #going with default values for mempool="./mempool",statefile="./state.json",descr=None
        return tx

    def transfersec(self):
        transferdata={"asset1_code": self.contractparams['contractspecs']['sec_token_code'],
                        "asset2_code": 0,
                        "wallet1": self.contractparams['contractspecs']['secprovider'],
                        "wallet2": self.contractaddress,
                        "asset1_number": self.contractparams['contractspecs']['sec_token_amount'],
                        "asset2_number": 0}
        tx=self.create_tx(5,transferdata,"INR",0.0) #going with default values for mempool="./mempool",statefile="./state.json",descr=None
        return tx

    def checkstatus(self):
        #returns status without adding a chain transaction; status is one of : awaiting tx confirmations, awaiting deployment, live, terminated, etc
        status=self.contractparams['status']
        if status==0:
            print("Contract not yet set up")
            return 0
        if status==1:
            print("Contract set up and awaiting deployment")
            return 1
        if status==2:
            print("Contract set up and deployed, currently live")
            return 2
        if status==-1:
            print("Contract terminated. Not live")
            return -1

    def reverseandterminate(self):
        #this reverses all transfer transactions into the contract address and terminates the contract; to be used when cancelling a contract before deploying
        # it can only be initiated by original smart contract creator
        if self.contractparams['status']==2:
            print("This is a deployed contract, cannot reverse it. Exiting.")
            return False
        if self.contractparams['status']==0:
            print("This contract is yet to be setup, nothing is expected to be in its wallet. Exiting.")
            return False
        # it is assumed that a contract that is in any other state will check its balances and return it to where they came from
        # the contract will assume that senders are as per the original params and will not take new arguments about where to send the balances
        # technically a defunt contract can still return funds back to where they came from if this function is called. Useful if funds are stuck
        # also, an expired but not terminated contract can also be made to return tokens to their original senders        
        contbalances=self.getcontaddbal();
        contloanbal=contbalances['contloanbal']
        conttokbal=contbalances['conttokbal']
        contsecbal=contbalances['contsecbal']

        #########
        #code for deployment
        # 1. code to open the balances db and transfer lent tokens from contract to lender, and loan tokens from contract to borrower and sectokens from contract to secprovider
        # update the status in contracts db as well
        #########
        self.terminate();
        print("Reversed and terminated smart contract - ",self.template,"with address ",self.contractaddress)
        return True
        
    def terminate(self):
        if self.contractparams['status']==2:
            print("This is a deployed contract, cannot terminate it while it is live. Exiting.")
            return False
        self.contractparams['status']=-1     # changed from 1 (setup done) to -1 (terminated)
        ##### code to update the db for change in status
        #########
        return True

    def close(self):
        # this is to be used when a contract has run its course and has carried out what's required of it and is no longer required
        if self.contractparams['status']==3:
            print("Contract expired. Terminating.")
            flag=self.terminate()
            if flag:
                print("Contract ",self.contractaddress," has been terminated.")
                return True
            else:
                print("Couldn't terminate despite expired status; investigate.")
                return False
        print("Not an expired contract. Not closing.")
        return False
    
    def check_default(self):
    #    due_date_ts=datetime.strptime(self.contractparams['contractspecs']['start_date'], "%Y-%m-%d %H:%M:%S")+datetime.timedelta(days=int(self.contractparams['contractspecs']['tenor']))
        if datetime.datetime.now() < datetime.strptime(self.contractparams['contractspecs']['due_date'], "%Y-%m-%d %H:%M:%S"):
            return False;	# not in default since due date is still away
        contbalances=self.getcontaddbal();
        if contbalances['conttokbal']>=self.contractparams['contractspecs']['repayment']:
            return False;   #i.e. not a default
        else:
            return True;    # default

    def run(self,callparams):
        #this is triggered by EOA or time and checks where things stand as of that date and executes different paths based on that.
        if self.contractparams['status']!=2:
            print("Not a live contract. Exiting.")
            return False
        contbalances=self.getcontaddbal()
        if self.check_default:  #default case
            print("Default has happened, executing collateral transfer to lender and loantoken transfer to secprovider")
            #### code for sell_collateral etc
            #### in phase-1 we will simply transfer the collateral to the lender and close the loan
            #### transfer sectokens of amount contbalances['contsecbal'] to self.contractparams['contractspecs']['lenderwallet']
            #### loantokens of amount contbalances['contloanbal'] to self.contractparams['contractspecs']['secprovider']
            # the logic is that the loan is now transferred to the security provider who can choose to do with it as she pleases
            self.scorechange(True); #update the score in trust network
        else:   #not in default, so either due date is past and tokens are in the account or due date is still away
            if datetime.datetime.now() >= datetime.strptime(self.contractparams['contractspecs']['due_date'], "%Y-%m-%d %H:%M:%S"):
                print("Due date is past. Paying all tokens onwards to lender, borrower and secprovider and closing the loan.")
                nettokens= contbalances['conttokbal'] - self.contractparams['contractspecs']['repayment']    #non-default case, so has to be +ve or 0
                #### open state db and make the following transfers from the self.contractaddress
                #### lenttokens of amount self.contractparams['contractspecs']['repayment'] to self.contractparams['contractspecs']['lenderwallet']
                #### loantokens of amount contbalances['contloanbal'] to self.contractparams['contractspecs']['borrowerwallet']
                #### lenttokens of amount nettokens to self.contractparams['contractspecs']['borrowerwallet']
                #### sectokens of amount contbalances['contsecbal'] to self.contractparams['contractspecs']['secprovider']
                self.contractparams['status']=3     #change this in the state db as well, in case the closure fails.
                self.close()
                self.scorechange(False); #update the score in trust network
                return True
            else:
                print("Due date still away. Returning without any execution.")
                return True     #valid run but nothing to do
            
    def sell_collateral(self, tokcode=None):
        # this requires connection into a decentralized marketplace - TBD
        if self.check_default['status']==True:	# there is default
            #### code for selling collateral
            pass

    def scorechange(self, defstatus):
        #update the trust score based on regular or defaulted execution
        pass

    def trigger_detokenization(self):
        pass
    
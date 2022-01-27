# class to create smart contract for creating stablecoins on Newrl
import codecs
from marshal import loads
from subprocess import call
import uuid
import ecdsa
from Crypto.Hash import keccak
import os
import json
import datetime
import time
import sqlite3
import hashlib

from ...constants import NEWRL_DB

class nusd1():
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class
    def __init__(self,contractaddress=None):
        self.template="nusd1"
        self.version=""
        self.address=contractaddress    #this is for instances of this class created for tx creation and other non-chain work
        if contractaddress:     #as in this is an existing contract
            con = sqlite3.connect(NEWRL_DB)
            cur = con.cursor()
            params = self.loadcontract(cur, contractaddress)  #this will populate the params for a given instance of the contract
            con.close()
        if not params or not contractaddress:   #either no contractaddress provided or new adddress not in db
            contractparams={}
            contractparams['creator']=""
            contractparams['ts_init']=0
            contractparams['name']=self.template
            contractparams['version']=self.version
            contractparams['actmode']="hybrid"
            contractparams['status']=0
            contractparams['next_act_ts']=0
            contractparams['signatories']=[]
            contractparams['parent']=""
            contractparams['oracleids']=[]
            contractparams['contractspecs']={}
            contractparams['legalparams']={}
            self.contractparams=contractparams

    def setup(self, cur, callparams):
        #this is called by a tx type 3 signed by the creator, it calls the function setp with parameters as params
        #setup implies a transaction for contract address creation
        contractparams= input_to_dict(callparams)
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
        if not self.address:    #no pre-set address, need to create a new one
            self.address = create_contract_address()

        if contractparams['name']!=self.template:
            print("Mismatch in contractname. Not creating a new contract.")
            return False
    #    if contractparams['version']!=self.version:
    #        print("Mismatch in contract version. Not creating a new contract.")
    #        return False
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
        signstr=json.dumps(contractparams['signatories'])
        oraclestr = json.dumps(contractparams['oracleids'])
        qparams=(self.address,
                contractparams['creator'],
                contractparams['ts_init'],
                contractparams['name'],
                contractparams['version'],
                contractparams['actmode'],
                cstatus,
                contractparams['next_act_ts'],
                signstr,
                contractparams['parent'],
                oraclestr,
                sdestr,
                cspecs,
                legpars
                )
        cur.execute(f'''INSERT INTO contracts
                (address, creator, ts_init, name, version, actmode, status, next_act_ts, signatories, parent, oracleids, selfdestruct, contractspecs, legalparams)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', qparams)
        return self.address

    def loadcontract(self, cur, contractaddress):
        #this loads the contract from the state db
        #it should take as input contractaddress and output the contractparams as they are in the db as of the time of calling it
        #the output will populate self.contractparams to be used by other functions
        contract_cursor = cur.execute('SELECT * FROM contracts WHERE address = :address', {
                    'address': contractaddress})
        contract_row = contract_cursor.fetchone()
        if not contract_row:
            return False
        #print(contract)
    #    self.contractparams=dict(contract_row)
        self.contractparams = {k[0]: v for k, v in list(zip(contract_cursor.description, contract_row))}
        self.contractparams['contractspecs']=json.loads(self.contractparams['contractspecs'])
        self.contractparams['legalparams']=json.loads(self.contractparams['legalparams'])
        self.contractparams['signatories']=json.loads(self.contractparams['signatories'])
        self.contractparams['oracleids'] = json.loads(self.contractparams['oracleids'])
        print("Loaded the contract with following data: \n",self.contractparams)
        return self.contractparams
        
    def deploy(self, cur, callparamsip):
        # carries out the SC execution steps upon instruction from a transaction - during updater run, post block inclusion
        callparams= input_to_dict(callparamsip)
        if self.contractparams['status'] != 1:    #the contract is not setup, i.e. is either yet to be setup, already deployed or terminated
            print("The contract is not in the post-setup stage. Exiting without deploying.")
            return False
        else:
            if self.sendervalid(callparams['sender'], self.deploy.__name__):
                self.contractparams['status'] = 2     # changed from 1 (setup done) to 2 (deployed and live)
                cur.execute(f'''UPDATE contracts SET status=? WHERE address=?''', (self.contractparams['status'], self.address))
                print("Deployed smart contract - ",self.template,"with address ",self.address)
                self.updateondeploy(cur)
                return True
            else:
                print("Sender not valid or not allowed this function call.")
                return False

    def updateondeploy(self, cur):
        if 'legaldochash' in self.contractparams['legalparams']:
            legaldochash = self.contractparams['legalparams']['legaldochash']
        else:
            legaldochash = None
        tokendata={"tokencode": "4242",
                   "tokenname": "NUSD1",
                   "tokentype": 1,
                   "tokenattributes": {"fiat_currency":"USD", "sc_address": self.address},
                   "first_owner": None,
                   "custodian": self.address,
                   "legaldochash": legaldochash,
                   "amount_created": None,
                   "value_created": 0,
                   "disallowed": [],
                   "tokendecimal":2,
                   "sc_flag": True
                   }
        add_token(cur, tokendata)

    def sendervalid(self, senderaddress, function):
        sendervalidity = False
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        if 'approved_senders' not in cspecs:
            return True
        for appr_sender in self.contractparams['contractspecs']['approved_senders']:
            if senderaddress == appr_sender['address']:
                if appr_sender['allowed'] == 'all' or function in appr_sender['allowed']:
                    sendervalidity = True
        return sendervalidity

    def send_nusd_token(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        recipient_address = callparams['recipient_address']
        sender = callparams['sender']
        value = callparams['value']
        print("callparams are ",callparams)
        try:
            value = float(value)
        except:
            print("Can't read value as a valid number.")
            return False
        if not is_wallet_valid(cur, recipient_address):
            print("Recipient address not valid.")
            return False
        if not self.sendervalid(sender, self.sendervalid.__name__):
            print("Sender is not in the approved senders list.")
            return False

        tokendata={"tokencode": "4242",
                   "first_owner": recipient_address,
                   "custodian": self.address,
                   "amount_created": int(value*100),
                   "value_created": value,
                   "tokendecimal":2
                   }
        add_token(cur, tokendata)
        
    def destroy_nusd_token(self,sender_address, value):
        pass        

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

def is_wallet_valid(cur, address):
    wallet_cursor = cur.execute('SELECT wallet_public FROM wallets WHERE wallet_address=?', (address, ))
    wallet = wallet_cursor.fetchone()
    if wallet is None:
        return False
    return True

def transfer_tokens_and_update_balances(cur, sender, reciever, tokencode, amount):
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    print("Sender is ",sender  ," and their balance is ", sender_balance)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
    print("Receiver is ",reciever  ," and their balance is ", reciever_balance)
    sender_balance = sender_balance - amount
    reciever_balance = reciever_balance + amount
    print("Amount is ", amount)
    print("Updating sender's balance with ", sender_balance)
    print("Updating reciever's balance with ", reciever_balance)
    update_wallet_token_balance(cur, sender, tokencode, sender_balance)
    update_wallet_token_balance(cur, reciever, tokencode, reciever_balance)
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    print("Sender is ",sender  ," and their balance is ", sender_balance)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
    print("Receiver is ",reciever  ," and their balance is ", reciever_balance)

def update_wallet_token_balance(cur, wallet_address, token_code, balance):
    cur.execute(f'''INSERT OR REPLACE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet_address, token_code, balance))

def update_trust_score(cur, personid1, personid2, new_score, tstamp):
    cur.execute(f'''INSERT OR REPLACE INTO trust_scores
				(src_person_id, dest_person_id, score, last_time)
				 VALUES (?, ?, ?, ?)''', (personid1, personid2, new_score, tstamp))

def add_wallet_pid(cur, wallet):
    # checking if this is a linked wallet or new one; for linked, no new personid is created
    linkedstatus =  wallet['specific_data']['linked_wallet'] if 'linked_wallet' in wallet['specific_data'] else False
    if linkedstatus:
        pid_cursor = cur.execute('SELECT person_id FROM person_wallet WHERE wallet_id=?', (wallet['specific_data']['parentaddress'], )).fetchone()
        pid = pid_cursor[0]
        if not pid:
            print("No personid linked to the parentwallet.")
            return False
    else:     #not a linked wallet, so create a new pid and update person table
        hs = hashlib.blake2b(digest_size=20)
        hs.update((wallet['wallet_address']).encode())
        pid = 'pi' + hs.hexdigest()
        query_params=(pid, time.mktime(datetime.datetime.now().timetuple()))
        cur.execute(f'''INSERT OR IGNORE INTO person
                    (person_id, created_time)
                    VALUES (?, ?)''', query_params)

    #for both new and linked wallet, update the wallet table and person_wallet table
    kyc_doc_json = json.dumps(wallet['kyc_docs'])
    data_json = json.dumps(wallet['specific_data'])
    query_params = (wallet['wallet_address'],
                    wallet['wallet_public'],
                    wallet['custodian_wallet'],
                    kyc_doc_json,
                    wallet['ownertype'],
                    wallet['jurisd'],
                    data_json
                    )
    cur.execute(f'''INSERT OR IGNORE INTO wallets
            (wallet_address, wallet_public, custodian_wallet, kyc_docs, owner_type, jurisdiction, specific_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', query_params)

    query_params=(pid, wallet['wallet_address'])
    cur.execute(f'''INSERT OR IGNORE INTO person_wallet
                (person_id, wallet_id)
                VALUES (?, ?)''', query_params)

def add_token(cur, token, txcode = None):
    tcodenewflag = False
    existingflag = False
    if 'tokencode' in token:    #creating more of an existing token or tokencode provided by user
        if token['tokencode'] and token['tokencode'] != "0" and token['tokencode'] != "":
            tid = cur.execute('SELECT tokencode FROM tokens WHERE tokencode=?', (token['tokencode'], )).fetchone()
            if tid: #tokencode exists, more of an existing token is being added to the first_owner
                tid = tid[0]
                existingflag = True
            else:
                tid = str(token['tokencode'])    #if provided code does not exist, it is considered new token addition
                existingflag = False
        else:   # mistakenly entered tokencode value as "" or "0" or 0
            tcodenewflag = True
            existingflag = False
    if 'tokencode' not in token or tcodenewflag:   # new tokencode needs to be created
        if not txcode:
            txcode = str(time.mktime(datetime.datetime.now().timetuple()))
        hs = hashlib.blake2b(digest_size=20)
        hs.update(txcode.encode())
        tid = 'tk' + hs.hexdigest()
        existingflag = False

    if not existingflag:    # new token to be created
        tokendecimal = token['tokendecimal'] if 'tokendecimal' in token else 0
        tokendecimal = int(tokendecimal)
        token_attributes_json = json.dumps(token['tokenattributes'])
        disallowedjason=json.dumps(token['disallowed'])
        query_params = (
            tid,
            token['tokenname'],
            token['tokentype'],
            token['first_owner'],
            token['custodian'],
            token['legaldochash'],
            token['amount_created'],
            token['value_created'],
            token['sc_flag'],
            disallowedjason,
            txcode,
            tokendecimal,
            token_attributes_json
            )
        cur.execute(f'''INSERT OR IGNORE INTO tokens
            (tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, 
            amount_created, value_created, sc_flag, disallowed, parent_transaction_code, tokendecimal, token_attributes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)
        if token['amount_created']:
            update_wallet_token_balance(
                cur, token['first_owner'], tid, token['amount_created'])

    # now update balance for case of more of existing created
    else:
        if token['first_owner'] and token['amount_created']:
            added_balance = int(token['amount_created'] or 0)
            current_balance = get_wallet_token_balance(cur, token['first_owner'], tid)
            balance = int(current_balance or 0) + added_balance
            update_wallet_token_balance(
                cur, token['first_owner'], tid, balance)
            update_token_amount(cur, tid, token['amount_created'])

    return True

def get_wallet_token_balance(cur, wallet_address, token_code):
    balance_cursor = cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
                    'address': wallet_address, 'tokencode': token_code})
    balance_row = balance_cursor.fetchone()
    balance = balance_row[0] if balance_row is not None else 0
    return balance

def update_token_amount(cur, tid, amt):
    if not amt:
        print("Nothing to add.")
        return True
    tok_val = cur.execute('SELECT tokencode FROM tokens WHERE tokencode = :tokencode', {
                    'tokencode': tid}).fetchone()
    if not tok_val:
        print("Tokencode ", tid, " does not exist.")
        return False
    balance_cursor = cur.execute('SELECT amount_created FROM tokens WHERE tokencode = :tokencode', {
                    'tokencode': tid})
    balance_row = balance_cursor.fetchone()
    if balance_row:
        cumul_amt = int(balance_row[0]) if balance_row[0] else 0
    else:
        cumul_amt = int(0)
    cumul_amt = cumul_amt + amt
#    cur.execute(f'''INSERT OR REPLACE INTO tokens
#				(tokencode, amount_created)
#				 VALUES (?, ?)''', (tid, cumul_amt))
    cur.execute(f'''UPDATE tokens SET amount_created=? WHERE tokencode=?''',(cumul_amt,tid))

    return True

def get_contract_from_address(cur, address):
    contractdata = cur.execute('SELECT * FROM contracts WHERE address = :address', {
                    'address': address}).fetchone()
    if not contractdata:
        print("Contract with address ", address, " does not exist.")
        return {}
    contract = dict(contractdata)
    return contract

def get_pid_from_wallet(cur, walletaddinput):
    pid_cursor = cur.execute('SELECT person_id FROM person_wallet WHERE wallet_id=?', (walletaddinput, ))
    pid = pid_cursor.fetchone()
    if pid is None:
        return False
    return pid[0]

def create_contract_address():
    private_key_bytes = os.urandom(32)
    key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
    key_bytes = key.to_string()
    public_key = codecs.encode(key_bytes, 'hex')
    public_key_bytes = codecs.decode(public_key, 'hex')
    hash = keccak.new(digest_bits=256)
    hash.update(public_key_bytes)
    keccak_digest = hash.hexdigest()
    address = 'ct' + keccak_digest[-40:]   # this overwrites the None value in the init call, whenever on-chain contract is setup
    return address

def input_to_dict(ipval):
    if isinstance(ipval, str):
        callparams=json.loads(ipval)
    else:
        callparams = ipval
    return callparams
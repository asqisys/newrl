# program to create and manage objects for wallets
import codecs
from re import T, X
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import json
import datetime
import binascii
import base64

import sqlite3

from .chainscanner import get_wallet_token_balance
from ..constants import ALLOWED_CUSTODIANS_FILE, MEMPOOL_PATH, NEWRL_DB


class Transactionmanager:
    def __init__(self):
        self.transaction = {
            'timestamp': str(datetime.datetime.now()),
            'trans_code': "0000",
            'type': 0,
            'currency': "INR",
            'fee': 0.0,
            'descr': None,
            'valid': 1,
            'specific_data': {}
        }

        self.signatures = []
        self.mempool = MEMPOOL_PATH
        self.validity = 0


    def getvalidadds(self):
        trans = self.transaction
        ttype = trans['type']
        validadds = []
        if ttype == 1:  # wallet creation, custodian needs to sign
            validadds.append(trans['specific_data']['custodian_wallet'])
        if ttype == 2:    # token creation, custodian needs to sign
            validadds.append(trans['specific_data']['custodian'])
        if ttype == 3:      #smart contract tx
            validadds = get_sc_validadds(trans)
        if ttype == 4:    # two way transfer; both senders need to sign
            validadds.append(trans['specific_data']['wallet1'])
            validadds.append(trans['specific_data']['wallet2'])
        if ttype == 5:    # one way transfer; only sender1 is needed to sign
            validadds.append(trans['specific_data']['wallet1'])
        if ttype == 6:      #score change transaction, only address1 is added, not address2
            validadds.append(trans['specific_data']['address1'])
        return validadds

    def transactioncreator(self, tran_data_all):
        # standard data concerns static fields, specific data covers fields that are type specific
        tran_data = tran_data_all['transaction']
        if not tran_data['timestamp']:
            self.transaction['timestamp'] = str(datetime.datetime.now())
        else:
            self.transaction['timestamp'] = tran_data['timestamp']

        self.transaction['type'] = tran_data['type']
        self.transaction['currency'] = tran_data['currency']
        self.transaction['fee'] = tran_data['fee']
        self.transaction['descr'] = tran_data['descr']
        self.transaction['valid'] = 1  # default at creation is unverified
        self.transaction['specific_data'] = tran_data['specific_data']
        trstr = json.dumps(self.transaction).encode()
        hs = hashlib.blake2b(digest_size=20)
        hs.update(trstr)
        self.transaction['trans_code'] = hs.hexdigest()
        self.signatures = tran_data_all['signatures']
        transaction_all = {'transaction': self.transaction,
                           'signatures': self.signatures}
        return transaction_all

    # this just loads the trasnactions passively, no change
    def set_transaction_data(self, transaction_data):
        self.transaction = transaction_data['transaction']
        self.signatures = transaction_data['signatures']
        return transaction_data
    
    def loadtransactionpassive(self, file):
        transactiondata = {}
        with open(file, "r") as readfile:
            print("Now reading from ", file)
            trandata = json.load(readfile)
        self.transaction = trandata['transaction']
        self.signatures = trandata['signatures']
        return trandata

    # this loads a transaction and creates a new trnsaction id
    def loadtransaction(self, file):
        transactiondata = {}
        with open(file, "r") as readfile:
            print("Now reading from ", file)
            trandata = json.load(readfile)
        newtrandata = self.transactioncreator(trandata)
        return newtrandata

    # dumps active transaction into a stated file or in mempool by default
    def dumptransaction(self, file=None):
        ts = self.transaction['timestamp']
        if not ts:
            ts = str(datetime.datetime.now())
        if not file:
            file = self.mempool+"transaction-" + \
                str(self.transaction['type'])+"-"+ts[0:10]+"-"+ts[-6:]+".json"
        transaction_all = {'transaction': self.transaction,
                           'signatures': self.signatures}
        with open(file, "w") as writefile:
            json.dump(transaction_all, writefile)
            print("Wrote to ", file)
        return file
    
    def get_transaction(self):
        transaction_all = {
            'transaction': self.transaction,
            'signatures': self.signatures
        }
        return transaction_all
    
    # this takes keybytes and not binary string and not base64 string
    def signtransaction(self, keybytes, address):
        msg = json.dumps(self.transaction).encode()
        sk = ecdsa.SigningKey.from_string(keybytes, curve=ecdsa.SECP256k1)
        msgsignbytes = sk.sign(msg)
        msgsign = base64.b64encode(msgsignbytes).decode('utf-8')
        self.signatures.append({'wallet_address': address, 'msgsign': msgsign})
    #	print("signed message ",msgsign,"and the key used was",keybytes)
        return sk.sign(msg)

    def verifysign(self, sign_trans, pubkeybytes, address):
        # the pubkey above is in bytes form
        #	print("using this pubkey to verify:",pubkeybytes)
        sign_trans_bytes = base64.decodebytes(sign_trans.encode('utf-8'))
        vk = ecdsa.VerifyingKey.from_string(pubkeybytes, curve=ecdsa.SECP256k1)
        message = json.dumps(self.transaction).encode()
    #	print("Sign validity: ",vk.verify(sign_trans,message))
    #	print("message is", message)
    #	print("sign_trans_byets are ",sign_trans_bytes)
        return vk.verify(sign_trans_bytes, message)

    def verifytransigns(self):
        # need to add later a check for addresses mentioned in the transaction (vary by type) and the signing ones
        validadds = self.getvalidadds()
        addvaliditydict = {}
        for valadd in validadds:
            addvaliditydict[valadd] = False
    #	allwallets=state
        prodflag = 1
        for signature in self.signatures:
            signaddress = signature['wallet_address']
    #		print("signaddress from signature: ",signaddress)
            addressvalidity = 0
            for valadd in validadds:
                if signaddress == valadd:  # the signature is of a relevant address for that transaction
                    addressvalidity = 1
            if not addressvalidity:
                print("Signature with address ", signaddress,
                      " is not relevant for this transaction.")
                continue
            msgsign = signature['msgsign']
            pubkey = get_public_key_from_address(signaddress)
    #		print("encoded pubkey from json file: ",pubkey)
            # here we decode the base64 form to get pubkeybytes
            pubkeybytes = base64.b64decode(pubkey)
        #	print("decoded bytes of pubkey",pubkeybytes)
    #		print("now verifying ",msgsign)
            if not self.verifysign(msgsign, pubkeybytes, signaddress):
                print("Signature for address ", signaddress, " is invalid")
                prodflag = prodflag*0
                addvaliditydict[signaddress] = False  # making doubly sure
                return False
            else:
                # for a valid address the signature is found
                addvaliditydict[signaddress] = True
                prodflag = prodflag*1
        if prodflag:
            print("All provided signatures of the message valid; still need to check if all required ones are provided")
        #	return True
        else:
            print("Some of the provided signatures not valid")
        #	return False
        # now checking if signatures for all valid addresses are covered
        validsignspresent = 0
        for valadd in validadds:
            if addvaliditydict[valadd]:
                validsignspresent += 1
            else:
                print(
                    "Either couldn't find signature or found invalid signature for ", valadd)
            #	valaddsignpresent=valaddsignpresent*0;	#any one signaure not being present will throw an error
        if prodflag and validsignspresent >= len(validadds):
            print("All provided signatures valid and all required signatures provided")
            return True
        else:
            print("Either some signatures invalid or some required ones missing")
            return False

#	def techvalidator(self):
        # write a bunch of code to check for timestamp, type, currency,fee, desr as specific fields and formats
        # valid should be set as -1 i.e. not yet validated and block_index as <=0 so not yet included
        # specific_data format is dependent on type and hence needs to be coded for each type

    def mempoolpayment(self, sender, tokencode):
        #	if not mempool:
        mempool = self.mempool
        filenames = os.listdir(mempool)
        mppayment = 0
        for filename in filenames:
            if "validation" in filename or ".json" not in filename:
                continue
            fl = mempool+filename
        #	self.loadtransaction
            with open(fl, "r") as readfile:
                trandata = json.load(readfile)['transaction']
            ttype = trandata['type']
            if ttype < 3:  # 0 is genesis, 1 is wallet creation, 2 is token creation
                continue
            if ttype == 5:  # unilateral transaction so will have only asset_1 number
                if sender == trandata['specific_data']['wallet1'] and trandata['specific_data']['asset1_code'] == tokencode:
                    mppayment += trandata['specific_data']['asset1_number']
            if ttype == 4:  # bilateral trasnaction so will have both aset_1 and asset_2 numbers
                if sender == trandata['specific_data']['wallet1'] and trandata['specific_data']['asset1_code'] == tokencode:
                    mppayment += trandata['specific_data']['asset1_number']
                if sender == trandata['specific_data']['wallet2'] and trandata['specific_data']['asset2_code'] == tokencode:
                    mppayment += trandata['specific_data']['asset2_number']

        #	need to incorporate the fee as well in future
        return mppayment

    def econvalidator(self):
        # start with all holdings of the wallets involved and add validated transactions from mempool
        # from mempool only include transactions that reduce balance and not those that increase
        # check if the sender has enough balance to spend
        self.validity = 0
        if self.transaction['type'] == 1:
            custodian = self.transaction['specific_data']['custodian_wallet']
            walletaddress=self.transaction['specific_data']['wallet_address']
            if not is_wallet_valid(custodian):
                print("No custodian address found")
            #	self.transaction['valid']=0
                self.validity = 0
            else:
                print("Valid custodian address")
#                if self.transaction['specific_data']['specific_data']['linked_wallet']:  #linked wallet
                if 'linked_wallet' in self.transaction['specific_data']['specific_data']:
                    linkedwalletstatus=self.transaction['specific_data']['specific_data']['linked_wallet']
                else:
                    linkedwalletstatus= False
                if linkedwalletstatus:
                    parentwalletaddress = self.transaction['specific_data']['wallet_specific_data']['parentaddress']
                    if custodian == parentwalletaddress:
                        self.validity = 1   #linking a new wallet is signed by existing wallet itself
                    else:
                        self.validity = 0   #other custodian cannot sign someone's linked wallet address
                else:   # this is a new wallet and person
                    if is_wallet_valid(walletaddress):
                        print("Wallet with address", walletaddress, " already exists.")
                        self.validity = 0
                    else:
                        self.validity = 1
                    # additional check for allowed custodian addresses; valid only for new wallet, not linked ones
                        if os.path.exists(ALLOWED_CUSTODIANS_FILE):
                            print("Found allowed_custodians file; checking against it.")
                            custallowflag = False
                            with open(ALLOWED_CUSTODIANS_FILE, "r") as custfile:
                                allowedcust = json.load(custfile)
                            for cust in allowedcust:
                                if custodian == cust['address']:
                                    print("Address ", custodian,
                                          " is allowed as a custodian.")
                                    custallowflag = True
                            if not custallowflag:
                                print("Could not find address ", custodian,
                                      " amongst allowed custodians.")
                                self.validity = 0

    #	self.validity=0
        if self.transaction['type'] == 2:  # token addition transaction
            firstowner = self.transaction['specific_data']['first_owner']
            custodian = self.transaction['specific_data']['custodian']
            fovalidity = False
            custvalidity = False
            if firstowner:
                if is_wallet_valid(firstowner):
                    print("Valid first owner")
                    fovalidity = True
                else:
                    fovalidity = False
            else:   # there is no first owner, transaction to create token only
                if self.transaction['specific_data']['amount_created']:
                    print("Amount created cannot be non-zero if there is no first owner.")
                    fovalidity = False  # amount cannot be non-zero if no first owner
                else:
                    fovalidity = True
            if is_wallet_valid(custodian):
                print("Valid custodian")
                custvalidity = True
            if not fovalidity:
                print("No first owner address found")
            #	self.transaction['valid']=0
                self.validity = 0
            if not custvalidity:
                print("No custodian address found")
                self.validity = 0
            if fovalidity and custvalidity:
                print("Valid first owner and custodian")
            #	self.transaction['valid']=1
            #   now checking for instances where more tokens are added for an existing tokencode
                self.validity = 1
                if 'tokencode' in self.transaction['specific_data']:
                    tcode = self.transaction['specific_data']['tokencode']
                    if tcode and tcode != "0" and tcode !="" and tcode!="string":
                        if is_token_valid(self.transaction['specific_data']['tokencode']):
                            existing_custodian = get_custodian_from_token(self.transaction['specific_data']['tokencode'])
                            if custodian == existing_custodian:
                                self.validity = 1   #tokencode exists and is run by the given custodian
                            else:
                                print("The custodian for that token is someone else.")
                                self.validity = 0
                        else:
                            print("Tokencode provided does not exist. Will append as new one.")
                            self.validity = 1   #tokencode is provided by user
                    else:
                        print("Tokencode provided does not exist. Will append as new one.")
                        self.validity = 1   #tokencode is provided by user

        if self.transaction['type'] == 3:
            self.validity = 1
            for wallet in self.transaction['specific_data']['signers']:
                if not is_wallet_valid(wallet):
                    self.validity = 0
            if 'participants' in self.transaction['specific_data']['params']:
                for wallet in self.transaction['specific_data']['params']['participants']:
                    if not is_wallet_valid(wallet):
                        self.validity = 0

    #	self.validity=0
        if self.transaction['type'] == 4 or self.transaction['type'] == 5:
            ttype = self.transaction['type']
            startingbalance1 = 0
            startingbalance2 = 0
            sender1 = self.transaction['specific_data']['wallet1']
            sender2 = self.transaction['specific_data']['wallet2']
            tokencode1 = self.transaction['specific_data']['asset1_code']
            token1mp = self.mempoolpayment(sender1, tokencode1)
            token1amt = max(
                self.transaction['specific_data']['asset1_number'], token1mp)
            sender1valid = False
            sender2valid = False

            # for ttype=5, there is no tokencode for asset2 since it is off-chain, there is no amount either
            if ttype == 4:  # some attributes of transaction apply only for bilateral transfer and not unilateral
                #	startingbalance2=0;
                tokencode2 = self.transaction['specific_data']['asset2_code']
                token2mp = self.mempoolpayment(sender2, tokencode2)
                token2amt = max(
                    self.transaction['specific_data']['asset2_number'], token2mp)

            # address validity applies to both senders in ttype 4 and 5; since sender2 is still receiving tokens
            sender1valid = is_wallet_valid(sender1)
            sender2valid = is_wallet_valid(sender2)
            if not sender1valid:
                print("Invalid sender1 wallet")
            #	self.transaction['valid']=0
                self.validity = 0
            #	return False
            if not sender2valid:
                print("Invalid sender2 wallet")
            #	self.transaction['valid']=0
                self.validity = 0
            #	return False

            # tokenvalidity applies for both senders only in ttype 4
            token1valid = False
            if ttype == 4:
                # by keeping it here, we ensure that no code refers to token2valid for type5
                token2valid = False
            token1valid = is_token_valid(tokencode1)
            token2valid = ttype == 4 and is_token_valid(tokencode2)
            if not token1valid:
                print("Invalid asset1 code")
                self.validity = 0
            if ttype == 4 and not token2valid:
                    print("Invalid asset1 code")
                    self.validity = 0
            if ttype == 4 and token1valid and token2valid:
                    print("Valid tokens")
                    self.validity = 1
            else:  # this is ttype=5
                if token1valid:
                    print("Valid tokens")
                    self.validity = 1

            if self.validity == 0 or not sender1valid or not sender2valid:
                print("Transaction not valid due to invalid tokens or addresses")
                return False

            # resetting to check the balances being sufficient, in futures, make different functions
            self.validity = 0

            startingbalance1 = get_wallet_token_balance(sender1, tokencode1)
            if ttype == 4:
                startingbalance2 = get_wallet_token_balance(sender2, tokencode2)
            if token1amt > startingbalance1:  # sender1 is trying to send more than she owns
                print("sender1 is trying to send,", token1amt, "she owns,",
                      startingbalance1, " invalidating transaction")
            #	self.transaction['valid']=0;
                self.validity = 0
            if ttype == 4:
                if token2amt > startingbalance2:  # sender2 is trying to send more than she owns
                    print(
                        "sender2 is trying to send more than she owns, invalidating transaction")
            #		self.transaction['valid']=0;
                    self.validity = 0
            if ttype == 4:
                if token1amt <= startingbalance1 and token2amt <= startingbalance2:  # double checking
                    print(
                        "Valid economics of transaction. Changing economic validity value to 1")
                #	self.transaction['valid']=1;
                    self.validity = 1
            if ttype == 5:
                if token1amt <= startingbalance1:
                    print(
                        "Valid economics of transaction. Changing economic validity value to 1")
                #	self.transaction['valid']=1;
                    self.validity = 1

        if self.transaction['type'] == 6:   #score change transaction
            ttype = self.transaction['type']
        #    personid1 = self.transaction['specific_data']['personid1']
        #    personid2 = self.transaction['specific_data']['personid2']
            wallet1 = self.transaction['specific_data']['address1']
            wallet2 = self.transaction['specific_data']['address2']
            wallet1valid = False
            wallet2valid = False

            wallet1valid = is_wallet_valid(wallet1)
            wallet2valid = is_wallet_valid(wallet2)
            if not wallet1valid or not wallet2valid:
                print("One of the wallets is invalid")
                self.validity = 0
            else:
            #    if get_pid_from_wallet(wallet1) != personid1 or get_pid_from_wallet(wallet2) != personid2:
                if not get_pid_from_wallet(wallet1) or not get_pid_from_wallet(wallet2):
                    print("One of the wallet addresses does not have a valid associated personids.")
                    self.validity = 0
                else:
                    if self.transaction['specific_data']['new_score'] < 0.0 or self.transaction['specific_data']['new_score'] > 3.0:
                        print("New_score is out of valid range.")
                        self.validity = 0
                    else:
                        self.validity = 1

        if self.validity == 1:
            return True
        else:
            return False  # this includes the case where valid=-1 i.e. yet to be validated

#	def legalvalidator(self):
        # check the token restrictions on ownertype and check the type of the recipient

def get_public_key_from_address(address):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    wallet_cursor = cur.execute('SELECT wallet_public FROM wallets WHERE wallet_address=?', (address, ))
    public_key = wallet_cursor.fetchone()
    if public_key is None:
        raise Exception('Wallet with address not found')
    return public_key[0]

def is_token_valid(token_code):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    token_cursor = cur.execute('SELECT tokencode FROM tokens WHERE tokencode=?', (token_code, ))
    token = token_cursor.fetchone()
    if token is None:
        return False
    return True

def is_wallet_valid(address):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    wallet_cursor = cur.execute('SELECT wallet_public FROM wallets WHERE wallet_address=?', (address, ))
    wallet = wallet_cursor.fetchone()
    if wallet is None:
        return False
    return True

def get_wallets_from_pid(personidinput):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    wallet_cursor = cur.execute('SELECT wallet_id FROM person_wallet WHERE person_id=?', (personidinput, )).fetchall()
    if wallet_cursor is None:
        return False
    wallets = [dict(wlt) for wlt in wallet_cursor]
    return wallets

def get_pid_from_wallet(walletaddinput):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    pid_cursor = cur.execute('SELECT person_id FROM person_wallet WHERE wallet_id=?', (walletaddinput, ))
    pid = pid_cursor.fetchone()
    if pid is None:
        return False
    return pid[0]

def get_custodian_from_token(token_code):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    token_cursor = cur.execute('SELECT custodian FROM tokens WHERE tokencode=?', (token_code, ))
    custodian = token_cursor.fetchone()
    if custodian is None:
        return False
    return custodian[0]

def get_sc_validadds(transaction):
    validadds=[]
    funct = transaction['specific_data']['function']
    address = transaction['specific_data']['address']
    if not address: #the sc is not yet set up
        if funct == "setup":     # only setup function allowed in this case
            validadds.append(transaction['specific_data']['params']['creator'])
            return validadds
        else:
            print("Invalid call to a function of a contract yet to be set up.")
            return False
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    signatories = cur.execute('SELECT signatories FROM contracts WHERE address=?', (address, )).fetchone()
    con.close()
    if signatories is None:
        print("Contract does not exist.")
        return False
    functsignmap = json.loads(signatories[0])
    if funct in functsignmap:     #function is allowed to be called
        for signer in (transaction['specific_data']['signers']):    #checking if stated signer is in allowed list
            if not functsignmap[funct] or signer in functsignmap[funct]:
                validadds.append(signer)
            # a function may allow anyone to call or the signer may be present in the dictionary funcsignmap
        return validadds
    else:
        print("Either function is not valid or it cannot be called in a transaction.")
        return False
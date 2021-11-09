# class to create smart contract for loan with bullet repayment
import codecs
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import json
import datetime
import binascii
import base64

from codes.transactionmanager import Transactionmanager
from codes.kycwallet import Walletmanager

class SecLoan1(SCmaster):
    def __init__(self,filename=None):
        SCmaster.__init__(self,filename);

#        self.contractparams={};
#        if filename:
#            self.load_params(filename);
#        else:
#            print("No file to load. Exiting")
#            return False    #should we also add an exit() after this?
        
#        #initialization also implies a transaction for contract address creation
#        private_key_bytes = os.urandom(32)
#        key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
#        key_bytes = key.to_string()
#        public_key = codecs.encode(key_bytes, 'hex')
#        public_key_bytes = codecs.decode(public_key, 'hex')
#        hash = keccak.new(digest_bits=256)
#        hash.update(public_key_bytes)
#        keccak_digest = hash.hexdigest()
#        self.contractaddress = '0x' + keccak_digest[-40:]
#        # we have ignored the private key and public key of this because we do not want to transact through key-based signing for a contract
#        # now we need to update the contract parameters in SC database; for now we are appending to the allcontracts.json
#        contractdata={"contractaddress":self.contractaddress,
#                      "contractparams":self.contractparams,
#                      "ts_init":str(datetime.datetime.now())
                      }
#        #code to append contractdata into allcontracts.json / to be replaced by code for appending contractdata into allcontracts db

#    def load_params(self,filename):
#        with open filename as ipfile:
#            self.contractparams=json.load(ipfile);

    def deploy(self,name=None):	# carries out the loan execution steps upon inclusion of the transaction in a block
        #action1: token creation for the loan
        if not name:
            name="Secloantoken"+self.contractaddress[:5]
        tokendata={"tokencode": 0,
                   "tokenname": name,
                   "tokentype": 62,
                   "tokenattributes": self.contractparams,
                   "first_owner": self.contractparams['contractspecs']['lenderwallet'],
                   "custodian": self.contractparams['contractspecs']['borrowerwallet'],
                   "legaldochash": "",
                   "amount_created": self.contractparams['contractspecs']['loanamount'],
                   "value_created": self.contractparams['contractspecs']['loanamount'],
                   "disallowed": [],
                   "sc_flag": True}
        

    def create_loan_token(self):

    def calc_repayment(self):
        repayment=self.loanamount*(1+self.int_rate*self.tenor)
        return repayment;
    
    def check_default(self):
        if today<self.start_date+self.tenor:
            return {"check":True, "status":False};	# no need to check since due date is still away
        repayment=self.calc_repayment();
        if today>=self.start_date+self.tenor:
            try:
                if get_balance(self.contractwallet,self.tokencode)>=repayment:
                    return {"check":True, "status":False};	# managed to get balance and it is sufficient, hence no default
                else:
                    return {"check":True, "status":True};	# managed to get balance but it is insufficient, hence default
            except:
                print("Can't get balance of contract wallet; check status again")
                return {"check":False, "status":None};

    def sell_collateral(self):
        if self.check_default['check']==True:	# there is valid check
            if self.check_default['status']==True	# there is default

    def trigger_detokenization(self):

    def make_repayment(self, proportion=1.0):

    def release_collateral(self):
        
def sc_smartloan(filename=None):
# not sure if we need this.. just placeholder for now

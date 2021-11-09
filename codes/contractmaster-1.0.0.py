# parent class for all contracts
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

class SCmaster:
    def __init__(self,filename=None):
        if filename:
            self.load_params(filename);
        else:
            print("No file to load. Exiting")
            return False    #should we also add an exit() after this?
        
        #initialization also implies a transaction for contract address creation
        private_key_bytes = os.urandom(32)
        key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
        key_bytes = key.to_string()
        public_key = codecs.encode(key_bytes, 'hex')
        public_key_bytes = codecs.decode(public_key, 'hex')
        hash = keccak.new(digest_bits=256)
        hash.update(public_key_bytes)
        keccak_digest = hash.hexdigest()
        self.contractaddress = '0x' + keccak_digest[-40:]
        # we have ignored the private key and public key of this because we do not want to transact through key-based signing for a contract
        # now we need to update the contract parameters in SC database; for now we are appending to the allcontracts.json
        self.contractdata={"contractaddress":self.contractaddress,
                      "contractparams":self.contractparams,
                      "ts_init":str(datetime.datetime.now())
                      }
        #code to append contractdata into allcontracts.json / to be replaced by code for appending contractdata into allcontracts db

    def load_params(self,filename):
        with open filename as ipfile:
            self.contractparams=json.load(ipfile);

    def create_tx(self,mempool="./mempool",statefile="./state.json",txfilename,descr=None):
        transaction={'timestamp':str(datetime.datetime.now()),
                    'type':3,
                    'currency':"INR",
		    'fee':0.0 ,
                    'descr':descr,
                    'valid':1,
                    'block_index':0,
                    'specific_data':self.contractdata}
        # this section is to be re-written upon the database version conclusion
        trans=Transactionmanager(mempool, statefile);
        signatures=[]
        transactiondata={'transaction':transaction,'signatures':signatures}
        trans.transactioncreator(transactiondata);
        trans.dumptransaction(txfilename);  #the tx is created at the location txfilename

    def deploy(self):
        pass

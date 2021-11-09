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
        #action1: address creation for the contract
        SCmaster.__init__(self,filename);

    def create_child_txs(self):
        #action2: token creation for the loan
        loantokentx=self.create_loan_token();
        lendtransfertx=self.transferlend();
        sectransfertx=self.transfersec();
        return loantokentx,lendtransfertx,sectransfertx;
        
    def deploy(self,name=None):	# carries out the loan execution steps upon inclusion of the transaction in a block
        if getbalance(self.contractaddress,self.loantokencode)>= self.contractparams['contractspecs']['loanamount'] and getbalance(self.contractaddress,self.contractparams['contractspecs']['tokencode'])>= self.contractparams['contractspecs']['loanamount'] and getbalance(self.contractaddress,self.contractparams['contractspecs']['sec_token_code']>=self.contractparams['contractspecs']['sec_token_amount']:
            #code for deployment
            pass

    def create_loan_token(self):
        name="Secloantoken"+self.contractaddress[:5]
        tokendata={"tokencode": 0,
                   "tokenname": name,
                   "tokentype": 62,
                   "tokenattributes": self.contractparams,
                   "first_owner": self.contractaddress,   #first owner is contract address till the contract is executed
                   "custodian": self.contractparams['contractspecs']['borrowerwallet'],
                   "legaldochash": self.contractparams['legalparams'],
                   "amount_created": self.contractparams['contractspecs']['loanamount'],
                   "value_created": self.contractparams['contractspecs']['loanamount'],
                   "disallowed": [],
                   "sc_flag": True,
                   "sc_address": self.contractaddress}
        loantoken=tokenmanager();
        tx = loantoken.sccreate(tokendata);
        self.loantokencode = tx['transaction']['specific_data']['tokencode']
        return tx

    def transferlend(self):
        transferdata={'transaction':
                      {"timestamp": str(datetime.datetime.now()),
                      "trans_code": "000000",
                      "type": 5,
                      "currency": "INR",
                      "fee": 0.0,
                      "descr": "",
                      "valid": 1,
                      "block_index": 0,
                      "specific_data": {"asset1_code": self.contractparams['contractspecs']['tokencode'],
                                        "asset2_code": 0,
                                        "wallet1": self.contractparams['contractspecs']['lenderwallet'],
                                        "wallet2": self.contractaddress,
                                        "asset1_number": self.contractparams['contractspecs']['loanamount'],
                                        "asset2_number": 0}},
                      "signatures":[]}
        translend=Transactionmanager()
        tx=translend.transactioncreator(transferdata)
        return tx

    def transfersec(self):
        transferdata={'transaction':
                      {"timestamp": str(datetime.datetime.now()),
                      "trans_code": "000000",
                      "type": 5,
                      "currency": "INR",
                      "fee": 0.0,
                      "descr": "",
                      "valid": 1,
                      "block_index": 0,
                      "specific_data": {"asset1_code": self.contractparams['contractspecs']['sec_token_code'],
                                        "asset2_code": 0,
                                        "wallet1": self.contractparams['contractspecs']['secprovider'],
                                        "wallet2": self.contractaddress,
                                        "asset1_number": self.contractparams['contractspecs']['sec_token_amount'],
                                        "asset2_number": 0}},
                      "signatures":[]}
        transsec=Transactionmanager()
        tx=transsec.transactioncreator(transferdata)
        return tx

    def checkstatus(self):
        #returns status without adding a chain transaction; status is one of : awaiting tx confirmations, awaiting deployment, live, terminated, etc
        pass

    def 
    
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

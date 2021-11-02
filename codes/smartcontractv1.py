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

from transactionmanager import Transactionmanager

class Smartloan:
    def __init__(self,filename=None):
        self.loandata={};
        if filename:
            self.load_params(filename);
        else:
            self.loandata={
                "tokencode"=0;	#the token that is borrowed, typically smt
                "loanamount"=0;	# amount borrowed of that token in numbers
                "int_rate"=0;	# absolute value of annual interest rate, annually compounded, stated in percent and two decimals as integer
                "start_date"=None;	# date of lending
                "tenor"=0;		# tenor in days
                "ltv"=0;		# loan to value ratio, stated in percent and two decimals as integer
                "sec_token_code"=0;	# token code of security used; if left blank or 0, the loan is unsecured
                "sec_token_amount"=0;	# amount in number of tokens of security
                "borrowerwallet"=None;	# borrower, typically single
                "lenderwallet"=None;	# lender, can be a person or a smart contract
                "secprovider"=None;	# security provider, can be a person or a smart contract
                "special_params"={}	# generic dict of additional parameters that users can apply as desired
                    }


    def load_params(self,filename):
        with open filename as ipfile:
            self.loandata=json.load(ipfile);

    # smart contracts move through a two step process of proposal and execution
    # the propose_tx function will create a tx of type 3 that is the definition of the contract; this can be proposed by any valid wallet
    
    def create_loan_transaction(self):	#creates the contract wallet and relevant transactions for signing by participants
        transaction={'timestamp':str(datetime.datetime.now()),
                    'type':3,
                    'currency':"INR",
		    'fee':0.0 ,
                    'descr':"New smartloan creation",
                    'valid':1,
                    'block_index':0,
                    'specific_data':self.loandata}
        trans=Transactionmanager(mempool, statefile);
        signatures=[]
        transactiondata={'transaction':transaction,'signatures':signatures}
        trans.transactioncreator(transactiondata);
        trans.dumptransaction();

    def propose_loan_tx(self):  #carries out the applicable tx creation for a smart contract
        #create a contract wallet
        
        #list the SC in SC database
        #create the child transactions required for the smart contract execution


    def sign_loan_transaction(self):	# signs a given loan transaction using the transaction signature code
        


    def validate_loan_transaction(self):	# verifies the balances of lender and security providers

    def execute_loan_transaction(self):	# carries out the loan execution steps upon inclusion of the transaction in a block

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
        

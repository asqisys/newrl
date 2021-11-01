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
#        self.tokencode=2;	#the token that is borrowed, typically smt
#        self.loanamount=0;	# amount borrowed of that token in numbers
#        self.int_rate=0.05;	# absolute value of annual interest rate, annually compounded
#        self.start_date=None;	# date of lending
#        self.tenor=365;		# tenor in days
#        self.ltv=0.5;		# loan to value ratio, used only for enforcing the condition as applicable
#        self.sec_token_code=0;	# token code of security used
#        self.sec_token_amount=0;	# amount in number of tokens of security
#        self.borrowerwallet=None;	# borrower, typically single
#        self.lenders=[];		# lender, can be one or more
#        self.secproviders=[];	# security providers, can include borrower and zero or more others
#        self.special_params={}		# generic dict of additional parameters that users can apply as desired
        if filename:
            self.load_params(filename);

    def load_params(self,filename):
        with open filename as ipfile:
            self.loandata=json.load(ipfile);
#        self.tokencode=loandata['tokencode'];	#the token that is borrowed, typically smt
#        self.loanamount=loandata['loanamount'];	# amount borrowed of that token in numbers
#        self.int_rate=loandata['int_rate'];	# absolute value of annual interest rate, annually compounded
#        self.start_date=loandata['start_date'];	# date of lending
#        self.tenor=loandata['tenor'];		# tenor in days
#        self.ltv=loandata['ltv'];		# loan to value ratio, used only for enforcing the condition as applicable
#        self.sec_token_code=loandata['sec_token_code'];		# token code of security used
#        self.sec_token_amount=loandata['sec_token_amount'];	# amount in number of tokens of security
#        self.borrowerwallet=loandata['borrowerwallet'];		# borrower, typically single
#        self.lenders=loandata['lenders'];			# lender wallets and their proportions, can be one or more
#        self.secproviders=loandata['secproviders'];	        # security providers, can include borrower and zero or more others
#        self.special_params=loandata['special_params']		# generic dict of additional parameters that users can apply as desired

    def create_loan_transaction(self):	#creates the loan transaction for signing by participants
        transaction={'timestamp':str(datetime.datetime.now()),
                    'type':6,
                    'currency':"INR",
		    'fee':0.0 ,
                    'descr':"New smartloan creation",
                    'valid':1,
                    'block_index': 0,
                    'specific_data':self.loandata}
        trans=Transactionmanager(mempool, statefile);
        signatures=[]
        transactiondata={'transaction':transaction,'signatures':signatures}
        trans.transactioncreator(transactiondata);
        trans.dumptransaction();

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
        

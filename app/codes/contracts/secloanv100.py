# class to create smart contract for loan with bullet repayment
from .contract_master import ContractMaster
from ..db_updater import *
from ...constants import ZERO_ADDRESS

class SecLoan1v100(ContractMaster):
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class
    def __init__(self,contractaddress=None):
        self.template="secloan1"
        self.version="1.0.0"
        self.address=contractaddress
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateanddeploy(self, cur):
        '''can be called only by borrower and is akin to signing the borrowing contract'''
        lent_amount=get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['tokencode'])
        security_amount=get_wallet_token_balance(cur, self.address,self.contractparams['contractspecs']['sec_token_code'])
        if lent_amount>= self.contractparams['contractspecs']['loanamount'] and security_amount >= self.contractparams['contractspecs']['sec_token_amount']:
            self.create_loan_token(cur)
            self.contractparams['next_act_ts'] = self.contractparams['contractspecs']['due_date']   #this is so only for bullet repayment, else this will be emi date
            cur.execute(f'''UPDATE contracts SET next_act_ts=? WHERE address=?''', (self.contractparams['next_act_ts'], self.address))
            return True
        else:
            print("One of the pre-conditions yet to be fulfilled, not deploying.")
            return False

    def create_loan_token(self, cur):
        name="Secloantoken"+self.address[:5]
        tokencode="ln"+self.address[1:]
        contractspecs=json.loads(self.contractparams['contractspecs'])
        tokendata={"tokencode": tokencode,
                   "tokenname": name,
                   "tokentype": 62,
                   "tokenattributes": self.contractparams,
                   "first_owner": contractspecs['lenderwallet'],
                   "custodian": self.address,
                   "legaldochash": self.contractparams['legalparams'],
                   "amount_created": contractspecs['loanamount'],
                   "value_created": contractspecs['loanamount'],
                   "disallowed": [],
                   "tokendecimal":0,
                   "sc_flag": True,
                   "sc_address": self.address}
        add_token(cur, tokendata, self.contractparams['parent'])
        return True

    def close_balances_and_terminate(self, cur):
        '''can be called externally only by borrower or internally - closes out balances in favor of lender and secprovider'''
        if self.contractparams['status']==2:
            print("This is a deployed contract, cannot reverse it. Exiting.")
            return False
        if self.contractparams['status']==0:
            print("This contract is yet to be setup, nothing is expected to be in its wallet. Exiting.")
            return False
        sc_money_balance = get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['tokencode'])
        sc_sectoken_balance = get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['sec_token_code'])
        if sc_money_balance:
            transfer_tokens_and_update_balances(cur, self.address, self.contractparams['contractspecs']['lenderwallet'],self.contractparams['contractspecs']['tokencode'],sc_money_balance)
        if sc_sectoken_balance:
            transfer_tokens_and_update_balances(cur, self.address, self.contractparams['contractspecs']['secproviderwallet'],self.contractparams['contractspecs']['sec_token_code'],sc_sectoken_balance)
        status = self.terminate(cur)
        if status:
            print("Reversed and terminated smart contract - ",self.template,"with address ",self.address)
        else:
            print("Could not terminate contract. Investigate! Contact address: ",self.address)
        return True

    def check_default(self, cur, checktime, loantokencode):
        if not self.check_duedate(checktime):
            return False
        sc_money_balance = get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['tokencode'])
        sc_mbal_expected = (get_tokens_outstanding(cur, loantokencode) / self.contractparams['contractspecs']['loanamount']) * self.contractparams['contractspecs']['repayment']
        if sc_money_balance >= sc_mbal_expected:
            return False;   #i.e. not a default
        else:
            return True;    # default

    def check_duedate(self, checktime):
        if time.mktime(datetime.datetime.now().timetuple()) < checktime: #need to replace .now with global time
            return False    # checking time given is in the future
        if checktime < self.contractparams['contractspecs']['due_date']:    #assumes that due_date is unix epoch int
            return False;	# not in default since due date is still away
        return True

    def runsendervalid(self, senderaddress, senderbalance, amount = None):
        if senderaddress == self.contractparams['contractspecs']['borrowerwallet']:
            return True
        if not amount:
            return False
        if amount <= senderbalance:
            return True
        else:
            return False

    def run(self, cur, callparams):
        '''called by lenders with their loan tokens to get money or security tokens in return or by borrower to close things'''
        if self.contractparams['status']==3:
            print("Expired contract, terminating.")
            terminate_status = self.close_balances_and_terminate(cur)
            return terminate_status
        if self.contractparams['status']!=2:
            print("Not a live contract. Exiting.")
            return False
        if not self.check_duedate(callparams['checktime']):
            print("Not due date yet. Exiting")
            return False
        outstanding_loan_tokens = get_tokens_outstanding(cur, callparams['loantokencode'])
        sc_sectoken_balance = get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['sec_token_code'])
        if not outstanding_loan_tokens:
            print("No outstanding tokens, returning balance collateral tokens, terminating and exiting.")
            transfer_tokens_and_update_balances(cur, self.address,self.contractparams['contractspecs']['secproviderwallet'] ,self.contractparams['contractspecs']['sec_token_code'],sc_sectoken_balance)
            self.contractparams['status'] = 3
            cur.execute(f'''UPDATE contracts SET status=? WHERE address=?''', (self.contractparams['status'], self.address))
            terminate_status = self.close_balances_and_terminate(cur)
            return terminate_status

        senderbalance = get_wallet_token_balance(cur, callparams['callerwallet'],callparams['loantokencode'])
        if not self.runsendervalid(callparams['callerwallet'], senderbalance, callparams['amount']):
            print("Invalid caller for the run function.")
            return False
        sc_money_balance = get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['tokencode'])
        money_tokens_due_to_caller = int(callparams['amount']/outstanding_loan_tokens * sc_money_balance)
        outstanding_ratio = outstanding_loan_tokens / self.contractparams['contractspecs']['loanamount']
        repayment_due_total = outstanding_ratio * self.contractparams['contractspecs']['repayment']
        money_proportion = sc_money_balance / repayment_due_total
        if money_proportion >= 1.0:
            default_status = False
        else:
            default_status = True
        sec_tokens_due_total = min(outstanding_ratio * (1 - money_proportion) * self.contractparams['contractspecs']['sec_token_amount'], sc_sectoken_balance)
        sec_tokens_due_to_caller = int(sec_tokens_due_total * callparams['amount']/outstanding_loan_tokens)
        #sec_tokens_due_to_secprovider =int(sc_sectoken_balance * min(1.0, money_proportion) * callparams['amount']/outstanding_loan_tokens)

        transfer_tokens_and_update_balances(cur, self.address, callparams['callerwallet'],self.contractparams['contractspecs']['tokencode'],money_tokens_due_to_caller)
        transfer_tokens_and_update_balances(cur, self.address, callparams['callerwallet'],self.contractparams['contractspecs']['sec_token_code'],sec_tokens_due_to_caller)
        transfer_tokens_and_update_balances(cur, callparams['callerwallet'], ZERO_ADDRESS , callparams['loantokencode'], callparams['amount'])

        self.scorechange(default_status, callparams['callerwallet'], self.contractparams['contractspecs']['borrowerwallet'])

    def scorechange(self, defstatus, wallet_lender, wallet_borrower):
        #update the trust score based on regular or defaulted execution
        pass
    
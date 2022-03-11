# class to create smart contract for loan with bullet repayment
from re import X
from .contract_master import ContractMaster
from ..db_updater import *

class SecLoan1v100(ContractMaster):
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class
    def __init__(self,contractaddress=None):
        self.template="secloan1"
        self.version="1.0.0"
        self.address=contractaddress
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateanddeploy(self, cur):
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
                   "first_owner": self.address,
                   "custodian": contractspecs['borrowerwallet'],
                   "legaldochash": self.contractparams['legalparams'],
                   "amount_created": contractspecs['loanamount'],
                   "value_created": contractspecs['loanamount'],
                   "disallowed": [],
                   "tokendecimal":0,
                   "sc_flag": True,
                   "sc_address": self.address}
        add_token(cur, tokendata, self.contractparams['parent'])
        return True

    def reverseandterminate(self, cur):
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
        status = self.terminate(cur)
        if status:
            print("Reversed and terminated smart contract - ",self.template,"with address ",self.address)
        else:
            print("Could not terminate contract. Investigate! Contact address: ",self.address)
        return True

    def check_default(self, cur, checktime):
        if time.mktime(datetime.datetime.now().timetuple()) < checktime: #need to replace .now with global time
            return False    # checking time given is in the future
        if checktime < self.contractparams['contractspecs']['due_date']:    #assumes that due_date is unix epoch int
            return False;	# not in default since due date is still away
        sc_money_balance = get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['tokencode'])
        if sc_money_balance >= self.contractparams['contractspecs']['repayment']:
            return False;   #i.e. not a default
        else:
            return True;    # default

    def run(self, cur, callparams):
        #this is triggered by EOA or time and checks where things stand as of that date and executes different paths based on that.
        if self.contractparams['status']!=2:
            print("Not a live contract. Exiting.")
            return False
        sc_money_balance = get_wallet_token_balance(cur,self.address,self.contractparams['contractspecs']['tokencode'])
        if self.check_default(cur, callparams['checktime']):  #default case
            print("Default has happened, updating contract default status to True.")
            ## code to update contractspecs['default'] to True

            #### code for sell_collateral etc can be triggered post this base don callparams
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
    
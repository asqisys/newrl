# Abstract Class for creating DAOs
import json

from . import Utils
from .contract_master import ContractMaster
from .dao_main_template_validator import create_proposal, vote_on_proposal
from ..db_updater import *
from abc import ABCMeta, abstractmethod

import importlib


class DaoMainTemplate(ContractMaster):
    __metaclass__ = ABCMeta
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of

    # this class

    def __init__(self, contractaddress):
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    @abstractmethod
    def update_and_deploy(self):
        raise NotImplementedError("Must override updateAndDeploy")

    def create_proposal(self, cur, callparamsip):
        # Method For Creating Prosposal

        callparams = input_to_dict(callparamsip)
        callparams['address']=self.address
        create_proposal(cur, callparams)
        dao_pid = get_pid_from_wallet(cur, self.address)
        # TODO max votes for now is hard coded
        cur.execute(f'''INSERT OR REPLACE INTO PROPOSAL_DATA
                    (dao_person_id, function_called,params,voting_start_ts,voting_end_ts,total_votes,status)
                    VALUES (?, ? ,? ,? ,? ,? ,? )''', (
            dao_pid, callparams['function_called'], json.dumps(callparams['params']), callparams['voting_start_ts'],
            callparams['voting_end_ts'], 10, 0))
        prop_id = cur.lastrowid
        response = {
            "status": 200,
            "proposal_id": prop_id
        }
        return response

    def vote_on_proposal(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        # ToDO Voting to be saved in
        callparams['address']=self.address
        # vote_on_proposal(cur, callparams)
        if self.valid_member(cur, callparams):
            
            member_pid = get_pid_from_wallet(cur,callparams['function_caller'][0]['wallet_address'])
            proposal_id=callparams['proposal_id']
            voter_db_data = cur.execute('''Select voter_data as "voter_data",yes_votes as "yes_votes",no_votes as "no_votes",abstain_votes as "abstain_votes",total_votes as "total_votes",function_called as "function_called"  from proposal_data where proposal_id = ?''', (proposal_id,))
            voter_db_data=voter_db_data.fetchone()


            # Initializing  the voter_db_data variable
            if (voter_db_data[0] is None):
                voter_db_data = ['{}', 0, 0, 0,voter_db_data[4],voter_db_data[5]]
            voter_data = input_to_dict(json.loads(voter_db_data[0]))
            yes_votes = voter_db_data[1]
            no_votes = voter_db_data[2]
            abstain_votes = voter_db_data[3]
            total_votes = voter_db_data[4]
            function_called = voter_db_data[5]
            if(self.duplicate_check(voter_db_data[0],member_pid)):


                if(callparams['vote']==-1):
                    no_votes=no_votes+1
                elif(callparams['vote']==1):
                    yes_votes=yes_votes+1
                else:
                    abstain_votes = abstain_votes + 1
                

                voter_data[member_pid]={"vote":callparams['vote'],"weight":None}
                cur.execute(f'''update proposal_data set voter_data=?,yes_votes=?,no_votes=?,abstain_votes=?  where proposal_id = ?''',(json.dumps(voter_data),yes_votes,no_votes,abstain_votes,proposal_id))
        

            else:
                return False
        
            #get voting scheme params from dao params
            cspecs = input_to_dict(self.contractparams['contractspecs'])
            voting_schemes = cspecs['voting_schemes']
            voting_scheme_params = None
            voting_scheme_selected=None
            for method in voting_schemes:
                if(method['function'] == function_called):
                    voting_scheme_params = method['params']
                    voting_scheme_selected=method['voting_scheme']
            
            #get total votes, current yes and no votes from proposal
            voting_specs = {
                'voting_scheme_params': voting_scheme_params,
                'current_yes_votes': yes_votes,
                'current_no_votes': no_votes,
                'total_votes':total_votes
            }

            funct = getattr(Utils, voting_scheme_selected)
            voting_result = funct(cur, voting_specs)
            #check if any condition is met
                #if yes (-1 or 1)
                #update the db
                #execute the function
            if(voting_result == 1):
                cur.execute('''update proposal_data set status = ? where proposal_id= ?''',("accepted",callparamsip['proposal_id']))
                self.execute(cur, callparamsip)
            if(voting_result == -1):
                cur.execute('''update proposal_data set status = ? where proposal_id= ?''',("rejected",callparamsip['proposal_id']))
        
        return False

    def execute(self, cur, callparamsip):
        # proposal ( funct , paramsip) - votes status
        # Getting proposal Data
        callparams = input_to_dict(callparamsip)
        proposal = cur.execute('''select function_called,params from proposal_data where  proposal_id=?''',
                               ("".join(str(callparams['proposal_id']))))
        proposal=proposal.fetchone()
        if (proposal is None):
            return False
        if self.check_status(cur,callparamsip):
            funct = getattr(self, proposal[0])
            funct(cur, proposal[1])
        else:
            return False

    def add_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        dao_pid = get_pid_from_wallet(cur, self.address)
        is_dao_exist = cur.execute(
            '''SELECT COUNT(*) FROM dao_membership WHERE dao_person_id LIKE ? AND member_person_id LIKE ?''',
            (dao_pid, callparams['member_person_id']))
        is_dao_exist=is_dao_exist.fetchone()
        if(is_dao_exist[0]==0):
            cur.execute('''INSERT OR REPLACE INTO dao_membership
                                (dao_person_id, member_person_id)
                                VALUES (?, ?)''', (dao_pid, callparams['member_person_id']))
            return {"status":200,"message":"Successfully added."}
        else:
            return {"status":500,"message":"Already exists."}

    def delete_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        dao_pid = get_pid_from_wallet(cur, self.address)
        # Sql code to update Membership table
        cur.execute('''DELETE FROM dao_membership 
                    WHERE dao_person_id= ? 
                    AND member_person_id= ? ''', (dao_pid, callparams['member_person_id']))
        return True

    def check_status(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        # if (cspecs['voting_scheme']):
        #     funct = getattr(Utils, cspecs['voting_scheme'])
        #     result = funct(cur, callparams)
        # else:
        #     result = Utils.voting_scheme_one(cur, callparams)
        # return result
        return True





    def valid_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        member_pid="".join(get_pid_from_wallet(cur,callparams['function_caller'][0]['wallet_address']))
        proposal = cur.execute('''Select count(*) from dao_membership where member_person_id like ?''', [member_pid])
        proposal=proposal.fetchone()
        if(proposal[0]==0):
            return False
        return True

    def duplicate_check(self,voter_data,member_pid):
        voter_data = input_to_dict(json.loads(voter_data))
        for voter in voter_data.keys():
            if(voter==member_pid):
                return False
        return True

    '''Token based methods'''
    
    def issue_token(self, cur, callparamsip):
        '''
        TODO
        params : walletId , txnHash, amount
        function : check txn validity and issue dao tokens to that pid
        '''

        #call params
        callparams = input_to_dict(callparamsip)
        transferTxn = callparams['transferTxn']
        recipient_address = callparams['recipient_address']
        amount = callparams['amount']

        #verify thr txn

        #issue tokens
        token_code = '_token' #TODO fetch dao name 
        tokendata = {"tokencode": cspecs['tokencode'],
                     "first_owner": recipient_address,
                     "custodian": self.address,
                     "amount_created": int(amount * 100),
                     "value_created": amount,
                     "tokendecimal": 2
                     }
        add_token(cur, tokendata)    
        pass


    def lock_tokens(self, cur, callparamsip):
        '''
        TODO 
        params : person_pid, dao_id, amount, txnHash (of transfer to dao)
        function : add a new row with pid and amount++ 
        '''

        callparams = input_to_dict(callparamsip)
        dao_id = callparams['dao_id']
        person_id = callparams['person_id']
        transferTxn = callparams['transferTxn']
        amount = callparams['amount']

        #update token stake table

    def get_token_lock_amount(self, cur, callparamsip):
        '''
        TODO
        params : pid , daoId, proposal_id
        function : check if any balance, add this proposal for that token status entry with current balance
        '''         
        
        callparams = input_to_dict(callparamsip)
        dao_id = callparams['dao_id']
        person_id = callparams['person_id']

        #fetch current token value locked
        
    def burn_token(self, cur, callapramsip):
        pass    

    def send_token(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        recipient_address = callparams['recipient_address']
        sender = callparams['sender']
        if sender:
            sender = self.address
        value = callparams['value']
        print("callparams are ", callparams)
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
        cspecs = input_to_dict(self.contractparams['contractspecs'])

        tokendata = {"tokencode": cspecs['tokencode'],
                     "first_owner": recipient_address,
                     "custodian": self.address,
                     "amount_created": int(value * 100),
                     "value_created": value,
                     "tokendecimal": 2
                     }
        add_token(cur, tokendata)    
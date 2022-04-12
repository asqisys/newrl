# Abstract Class for creating DAOs
import json

from . import Utils
from .contract_master import ContractMaster
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
        dao_pid = get_pid_from_wallet(cur, self.address)
        cur.execute(f'''INSERT OR REPLACE INTO PROPOSAL_DATA
                    (dao_person_id, function_called,params,voting_start_ts,voting_end_ts,max_votes,status)
                    VALUES (?, ?)''', (
            dao_pid, callparams['function_called'], callparams['params'], callparams['voting_start_ts'],
            callparams['voting_end_ts'], callparams['max_votes'], 0))
        prop_id = cur.insert_id()
        response = {
            "status": 200,
            "proposal_id": prop_id
        }
        return response

    def vote_on_proposal(self, cur, callparamsip):
        # ToDO Voting to be saved in
        if self.valid_member(cur, callparamsip):
            #check if already voted
            #update proposal db - votecount , proposal json
            #check if any condition is met
                #if yes (-1 or 1)
                #update the db
                #execute the function
            self.execute(cur, callparamsip)
            return True
        return False

    def execute(self, cur, callparamsip):
        # proposal ( funct , paramsip) - votes status
        # Getting proposal Data
        callparams = input_to_dict(callparamsip)
        proposal = cur.execute('''select * from proposal where dao_id=? and id=?''',
                               (self.address, callparams['proposal_id']))
        if (proposal is None):
            return False
        if self.check_status():
            proposal = json.loads(proposal)
            funct = getattr(self, proposal['function'])
            funct(cur, proposal['params'])
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
        if (cspecs['voting_scheme']):
            funct = getattr(Utils, cspecs['voting_scheme'])
            result = funct(cur, callparams)
        else:
            result = Utils.voting_scheme_one(cur, callparams)
        return result

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

    def burn_token(self, cur, callapramsip):
        pass

    def valid_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        member_pid=get_pid_from_wallet(callparams['function_caller'])
        proposal = cur.execute('''Select count(*) from dao_membership where member_person_id like ?''', member_pid)
        proposal=proposal.fetchone()
        if(proposal[0]==0):
            return False
        return True

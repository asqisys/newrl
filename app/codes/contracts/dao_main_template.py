# Abstract Class for creating DAOs

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
        if (callparams['proposal_desc']):
            pass
        pass

    def vote_on_proposal(self, cur, callparamsip):
        pass

    def execute(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        if self.check_status():
            module = importlib.import_module(
                ".codes.contracts." + cspecs['name'], package="app")
            sc_class = getattr(module, cspecs['name'])
            sc_instance = sc_class(cspecs['address'])
            #    sc_instance = nusd1(transaction['specific_data']['address'])
            funct = getattr(sc_instance, callparams['function'])
            funct(cur, callparams['params'])
        pass

    def add_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        dao_pid = get_pid_from_wallet(cur, self.address)
        # Sql code to update Membership table
        cur.execute('''INSERT OR REPLACE INTO dao_membership
                    (dao_person_id, member_person_id)
                    VALUES (?, ?)''', (dao_pid, callparams['member_person_id']))
        pass

    def delete_member(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        dao_pid = get_pid_from_wallet(cur, self.address)
        # Sql code to update Membership table
        cur.execute('''DELETE FROM dao_membership
                    WHERE doa_personid= ? 
                    AND member_person_id= ? ''', (dao_pid, callparams['member_person_id']))
        pass

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

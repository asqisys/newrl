# class to create smart contract for creating stablecoins on Newrl
import base64

from ecdsa import BadSignatureError

from .contract_master import ContractMaster
from ..db_updater import *
from ..transactionmanager import get_public_key_from_address, Transactionmanager


class AquaCredits(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "AquaCredits"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def validateCustodian(self, transaction, custodian_address, custodian_wallet, transaction_manager):
        valid = False
        matchedCustodian = [x for x in transaction['signatures'] if x['wallet_address'] == custodian_address][0]
        if (matchedCustodian is not None):
            try:
                sign_valid = transaction_manager.verify_sign(matchedCustodian['msgsign'],
                                                             custodian_wallet)
                valid = sign_valid
            except BadSignatureError:
                valid = False
            finally:
                return valid
        else:
            return False

    def issue_token(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        custodian_address = cspecs['custodian_address']
        custodian_wallet = base64.b64decode(get_public_key_from_address(custodian_address))
        token_code=callparams['token_code']
        recipient_address=callparams['recipient_address']
        amount=callparams['amount']
        print(custodian_address)
        print(callparams['function_caller'][0]['wallet_address'])
        if(callparams['function_caller'][0]['wallet_address']==custodian_address):
            tokendata = {
                "tokenname": token_code,
                "tokencode": token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": recipient_address,
                "custodian": custodian_address,
                "legaldochash": '',
                "amount_created": amount,
                "value_created": '',
                "disallowed": {},
                "sc_flag": False
            }
            add_token(cur, tokendata)


        return True

    def burn_token(self, cur, callparamsip):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        callparams = input_to_dict(callparamsip)
        custodian_address = cspecs['custodian_address']
        token_code = callparams['token_code']
        amount = callparams['amount']
        if (callparams['function_caller'][0]['wallet_address'] == custodian_address):
            tokendata = {
                "tokenname": token_code,
                "tokencode": token_code,
                "tokentype": '1',
                "tokenattributes": {},
                "first_owner": '',
                "custodian": custodian_address,
                "legaldochash": '',
                "amount_created": amount,
                "value_created": '',
                "disallowed": {},
                "sc_flag": False
            }
            add_token(cur, tokendata)





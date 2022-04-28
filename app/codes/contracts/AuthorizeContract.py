# class to create smart contract for creating stablecoins on Newrl
import base64

from ecdsa import BadSignatureError

from .contract_master import ContractMaster
from ..db_updater import *
from ..transactionmanager import get_public_key_from_address, Transactionmanager


class AuthorizeContract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "AuthorizeContract"
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

    def validate(self, cur, callparamsip):
        callparams = input_to_dict(callparamsip)
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        custodian_address = cspecs['custodian_address']
        custodian_wallet = base64.b64decode(get_public_key_from_address(custodian_address))

        transaction_manager = Transactionmanager()
        transaction_manager.set_transaction_data(callparams)

        return self.validateCustodian(callparams, custodian_address, custodian_wallet, transaction_manager)

    def modifyTokenAttributes(self, cur, callparamsip):
        if self.validate(cur, callparamsip):
            callparams = input_to_dict(callparamsip)
            query_params = (
                callparams['transaction']['tokenAttributes'],
                callparams['transaction']['tokenCode']

            )
            cur.execute(f'''UPDATE tokens SET token_attributes=? WHERE tokenCode=?''', query_params)
        else:
            return "Invalid Transaction: Error in custodian signature"

    def destroyTokens(self, sender_address, value):
        pass

    def createTokens(self, sender_address, value):
        pass

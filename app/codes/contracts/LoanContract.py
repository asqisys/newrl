# class to create smart contract for creating stablecoins on Newrl
from .contract_master import ContractMaster
from ..base.ScStateUpdater import ScStateUpdater
from ..db_updater import *
from ..entity.LoanEntity import LoanEntity


class LoanContract(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "LoanContract"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def add_detail(self, cur):
        cspecs = input_to_dict(self.contractparams['contractspecs'])
        le=LoanEntity(borrower=cspecs['borrower'],lender=cspecs['lender'],amount=cspecs['amount'])
        ScStateUpdater.updateState(le)
        pass


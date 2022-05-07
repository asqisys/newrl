"""Newrl network trust score management smart contract"""

from .contract_master import ContractMaster
from ..db_updater import *

class network_trust_manager(ContractMaster):
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self,contractaddress=None):
        self.template= "network_trust_manager"
        self.version=""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateondeploy(self, cur):
        pass

    def update_trust_scores(self, cur, callparamsip):
        pass
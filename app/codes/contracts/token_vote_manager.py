#class to manage token based voting
from .contract_master import ContractMaster

class token_vote_manager(ContractMaster):
    codehash = ""    # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "dao_manager"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)
    
    def updateondeploy(self, cur):
        pass

    

    
    def unlock_tokens(self, cur, callparamsip):
        '''
        TODO
        params : person_pid, dao_id,amount
        function : check if any proposals are pending and if yes return False, else transfer back the amount
        '''   
    
    def vote_with_token(self, cur, callparamsip):
        '''
        TODO
        params : pid , daoId, proposal_id
        function : check if any balance, add this proposal for that token status entry with current balance
        '''         

# class to create smart contract for creating stablecoins on Newrl
from .contract_master import ContractMaster
from ..db_updater import *

class Dao_Manager(ContractMaster):
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self,contractaddress=None):
        self.template= "Dao_Manager"
        self.version=""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateondeploy(self, cur):
        pass
  
    def create(self, cur, callparams):
        #create wallet and pid for contract or dao_sc_main
        contractaddress = create_contract_address();
        #cur?
        pid = add_wallet_pid(cur, contractaddress);
        #update dao db
            # create a row in doa membership with doa_personid, doa_name and founder_personid and dao_sc_address (ex : membersip_doa )
        self.create_dao_details(self,cur,callparams);
        #create contract instance for this new dao with params of doa sc main (contract table)
        pass

    def alter(self,cur,callParamsip):
        pass

    def terminate(self,cur,callParamsip):
        pass                

    def create_dao_details(self,cur, callParams):
        dao_personid=callParams['dao_personId']
        dao_name=callParams['dao_name']
        founder_personid=callParams['founder_personid']
        dao_sc_addres=callParams['dao_sc_addres']
        cur.execute(f'''INSERT OR REPLACE INTO doa
                    (doa_personid, doa_name, founder_personid, dao_sc_addres)
                    VALUES (?, ?, ?)''', (dao_personid, dao_name, founder_personid, dao_sc_addres))
# class to create smart contract for creating stablecoins on Newrl
from .contract_master import ContractMaster
from ..db_updater import *

class doa_manager(ContractMaster):
    codehash=""    #this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self,contractaddress=None):
        self.template= "doa_manager"
        self.version=""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateondeploy(self, cur):

  
    def create(doa_name, founders , dao_main_sc, doa_main_sc_version, contactSpecs):
        #create wallet and pid
        contractaddress = create_contract_address();
        #cur?
        pid = add_wallet_pid(cur, contractaddress);
        #update dao db
            # create a row in doa membership with doa_personid, doa_name and founder_personid and dao_sc_address (ex : membersip_doa )
        create_dao_details(doa_personid, doa_name, founder_personid, dao_sc_addres);
        #create contract instance for this new dao with params of doa sc main (contract table)
        pass

    def alter():
        pass

    def terminate():
        pass                

    def create_dao_details(cur, doa_personid, doa_name, founder_personid, dao_sc_address):
        cur.execute(f'''INSERT OR REPLACE INTO doa
                    (doa_personid, doa_name, founder_personid, dao_sc_addres)
                    VALUES (?, ?, ?)''', (doa_personid, doa_name, founder_personid, dao_sc_addres))
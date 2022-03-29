# class to create smart contract for creating stablecoins on Newrl
from .contract_master import ContractMaster
from ..db_updater import *


class Dao_Manager(ContractMaster):
    codehash = ""  # this is the hash of the entire document excluding this line, it is same for all instances of this class

    def __init__(self, contractaddress=None):
        self.template = "Dao_Manager"
        self.version = ""
        ContractMaster.__init__(self, self.template, self.version, contractaddress)

    def updateondeploy(self, cur):
        pass

    def create(self, cur, callparams):
        dao_params = input_to_dict(callparams)

        # create wallet and pid for contract or dao_sc_main
        dao_sc_address = create_contract_address();
        dao_person_id = add_wallet_pid(cur, dao_sc_address);


        # update dao db
        dao_name = dao_params['dao_name']
        founders_personid = json.dumps(dao_params['founders'])
        self.__create_dao_details(self, cur, dao_person_id, dao_name, founders_personid, dao_sc_address);

        # create contract instance for this new dao with params of dao sc main (contract table)
        contractparams = {}
        contractparams['status'] = 1
        contractparams['ts_init'] = time.mktime(datetime.datetime.now().timetuple())
        contractparams['address'] = dao_sc_address
        # ?
        contractparams['version'] = 1.0
        # sdestr?
        sdestr = 0 if not contractparams['selfdestruct'] else int(contractparams['selfdestruct'])
        cstatus = 0 if not contractparams['status'] else int(contractparams['status'])
        cspecs = json.dumps(dao_params['contractspecs'])
        legpars = json.dumps(contractparams['legalparams'])
        # signatories? voraclestr ?
        signstr = json.dumps(contractparams['signatories'])
        oraclestr = json.dumps(contractparams['oracleids'])
        qparams = (
        dao_sc_address, founders_personid, contractparams['ts_init'], dao_params['dao_name'], contractparams['version'],
        # actmode?
        contractparams['actmode'], cstatus,  # next_act_ts?
        contractparams['next_act_ts'], signstr,  # parent?
        contractparams['parent'], oraclestr, sdestr, cspecs, legpars)

        cur.execute(f'''UPDATE contracts SET status=? WHERE address=?''', (contractparams['status'], dao_sc_address))

        pass

    def alter(self, cur, callParamsip):
        pass

    def terminate(self, cur, callParamsip):
        pass

    def __create_dao_details(self, cur, dao_personid, dao_name, founder_personid, dao_sc_address):
        cur.execute(f'''INSERT OR REPLACE INTO dao_main
                    (dao_personid, dao_name, founder_personid, dao_sc_addres)
                    VALUES (?, ?, ?)''', (dao_personid, dao_name, founder_personid, dao_sc_address))

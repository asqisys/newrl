from .dao_main_template import DaoMainTemplate
from ..db_updater import *

class membership_dao_ver1(DaoMainTemplate):
    codehash=""

    def __init__(self, contractaddress=None,callParams={}):
        diction=input_to_dict(callParams)
        self.template= 'membership_dao_ver1'
        self.version='1.0.0'
        super().__init__(contractaddress)
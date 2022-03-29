from .dao_main_template import DaoMainTemplate
from ..db_updater import *


class MemberShipDaoVer1(DaoMainTemplate):
    def update_and_deploy(self):
        pass

    codehash = ""

    def __init__(self, contractaddress=None):
        self.template = 'memberShipDao'
        self.version = '1'
        super().__init__(contractaddress)

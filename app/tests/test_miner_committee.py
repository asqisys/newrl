import time
import sqlite3

from ..codes.auth.auth import get_wallet
from ..codes.minermanager import broadcast_miner_update, get_my_miner_status
from ..codes.db_updater import update_wallet_token_balance
from fastapi.testclient import TestClient
from ..ntypes import NUSD_TOKEN_CODE
from ..constants import NEWRL_DB
from ..nvalues import TREASURY_WALLET_ADDRESS
from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)


def test_mining_reward():
    assert None == get_my_miner_status()
    
    broadcast_miner_update()
    response = client.post('/run-updater')
    assert response.status_code == 200
    
    miner_info = get_my_miner_status()
    assert miner_info['wallet_address'] == get_wallet()['address']
    


def set_balance(wallet, token, balance):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    update_wallet_token_balance(cur, wallet, token, balance)
    con.commit()
    con.close()

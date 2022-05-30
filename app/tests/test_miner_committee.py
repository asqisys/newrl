import time
import sqlite3

from ..codes.blockchain import get_last_block_hash
from ..codes.utils import get_time_ms
from ..codes.auth.auth import get_wallet
from ..codes.minermanager import broadcast_miner_update, get_committee_for_current_block, get_miner_for_current_block, get_my_miner_status
from ..codes.db_updater import add_miner
from fastapi.testclient import TestClient
from ..constants import NEWRL_DB

from ..main import app

client = TestClient(app)


def test_mining_reward():
    assert None == get_my_miner_status()
    
    broadcast_miner_update()
    response = client.post('/run-updater')
    assert response.status_code == 200
    
    miner_info = get_my_miner_status()
    assert miner_info['wallet_address'] == get_wallet()['address']


def test_miner_selection():
    for i in range(0,20):
        _add_test_miner(i)
    
    last_block1 = get_last_block_hash()
    committee = get_committee_for_current_block()
    assert len(committee) == 6
    
    miner1 = get_miner_for_current_block()
    # Check if pseudo-random with block index as seed returns the same miner
    assert miner1['wallet_address'] == get_miner_for_current_block()['wallet_address']
    # my_wallet = get_wallet()
    # assert miner1['wallet_address'] == my_wallet['address']

    time.sleep(5)
    response = client.post('/run-updater')
    assert response.status_code == 200

    last_block2 = get_last_block_hash()

    assert last_block2['index'] == last_block1['index'] + 1
    miner2 = get_miner_for_current_block()

    # Hoping the miner changes for the new block. Totally random though
    assert miner1['wallet_address'] != miner2['wallet_address']


def _add_test_miner(i):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    add_miner(cur, f'0x0000{i}', '127.0.0.1', get_time_ms())
    con.commit()
    con.close()

def clear_miner_db():
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    cur.execute('delete from miners')
    con.commit()
    con.close()

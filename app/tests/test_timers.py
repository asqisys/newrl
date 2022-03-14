import os
import time
import sqlite3

from .test_p2p import _receive_block
from .test_miner_committee import _add_test_miner
from ..codes.updater import start_mining_clock
from ..codes.blockchain import get_last_block_hash
from ..codes.utils import get_time_ms
from ..codes.auth.auth import get_wallet
from ..codes.minermanager import broadcast_miner_update, get_committee_for_current_block, get_committee_list, get_miner_for_current_block, get_my_miner_status
from ..codes.db_updater import add_miner, update_wallet_token_balance
from fastapi.testclient import TestClient
from ..ntypes import NUSD_TOKEN_CODE
from ..constants import BLOCK_TIME_INTERVAL_SECONDS, NEWRL_DB
from ..nvalues import TREASURY_WALLET_ADDRESS
from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)


def test_mining_clock():
    broadcast_miner_update()
    response = client.post('/run-updater')
    assert response.status_code == 200

    response = client.get('/get-last-block-index')
    assert response.status_code == 200
    previous_block_index = int(response.text)

    start_mining_clock()

    time.sleep(BLOCK_TIME_INTERVAL_SECONDS + 2)

    response = client.get('/get-last-block-index')
    assert response.status_code == 200
    block_index = int(response.text)

    assert block_index == previous_block_index + 1

    for i in range(1, 3):
        _add_test_miner(i)
    # time.sleep(BLOCK_TIME_INTERVAL_SECONDS * 4)
    # os._exit(1)


def test_all_timers():
    broadcast_miner_update()
    response = client.post('/run-updater')
    assert response.status_code == 200

    broadcast_miner_update()
    response = client.post('/run-updater')
    
    response = client.get('/get-last-block-index')
    assert response.status_code == 200
    
    previous_block_index = int(response.text)
    _receive_block(previous_block_index + 1)
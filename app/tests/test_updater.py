import time
from app.codes.blockchain import get_last_block
from app.codes.p2p.sync_chain import receive_block

from app.tests.test_mempool import create_transaction

from .test_p2p import _receive_block
from .test_miner_committee import _add_test_miner
from ..codes.updater import mine, run_updater, start_mining_clock
from ..codes.minermanager import broadcast_miner_update
from fastapi.testclient import TestClient
from ..constants import BLOCK_TIME_INTERVAL_SECONDS

from ..main import app
from app.codes import updater

client = TestClient(app)


def test_mine():
    # _add_test_miner(1)
    create_transaction(0)
    block = mine(add_to_chain=True)
    # start_mining_clock(int(get_last_block_hash()['timestamp']))


def test_receive():
    create_transaction(0)
    block = run_updater()
    assert block is not None
    receive_block(block)

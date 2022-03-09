import sys
import time
import requests
import threading
from ..minermanager import broadcast_miner_update, get_miner_for_current_block, should_i_mine
from ...constants import BLOCK_RECEIVE_TIMEOUT_SECONDS, BLOCK_TIME_INTERVAL_SECONDS, MAX_ALLOWED_TIME_DIFF_SECONDS, NO_RECEIPT_COMMITTEE_TIMEOUT, TIME_DIFF_WITH_GLOBAL, TIME_MINER_BROADCAST_INTERVAL
from ..updater import mine_empty_block, run_updater


def no_receipt_timeout():
    print('No receipts received. Timing out.')


def mine():
    if should_i_mine():
        print('I am the miner for this block.')
        run_updater()
    else:
        miner = get_miner_for_current_block()
        print(f"Miner for current block is {miner['wallet_address']}. Waiting to receive block.")
        start_block_receive_timeout_clock()

def start_receipt_timeout():
    timer = threading.Timer(NO_RECEIPT_COMMITTEE_TIMEOUT, no_receipt_timeout)
    timer.start()


def start_mining_clock():
    mine()
    timer = threading.Timer(BLOCK_TIME_INTERVAL_SECONDS, start_mining_clock)
    timer.start()


def block_receive_timeout():
    miner = get_miner_for_current_block()
    print(f"Block receive timed out from miner {miner['wallet_address']}")
    block_index = mine_empty_block()['index']
    print(f"Mined new block {block_index}")


def start_block_receive_timeout_clock():
    timer = threading.Timer(BLOCK_RECEIVE_TIMEOUT_SECONDS, block_receive_timeout)
    timer.start()


def start_miner_broadcast_clock():
    print('Broadcasting miner update')
    broadcast_miner_update()
    timer = threading.Timer(TIME_MINER_BROADCAST_INTERVAL, start_miner_broadcast_clock)
    timer.start()

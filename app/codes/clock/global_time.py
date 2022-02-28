import sys
import time
import requests
import threading
from ..minermanager import broadcast_miner_update, should_i_mine
from ...constants import BLOCK_TIME_INTERVAL_SECONDS, MAX_ALLOWED_TIME_DIFF_SECONDS, NO_RECEIPT_COMMITTEE_TIMEOUT, TIME_DIFF_WITH_GLOBAL, TIME_MINER_BROADCAST_INTERVAL
from ..updater import run_updater


def get_global_epoch():
    # url = 'http://worldclockapi.com/api/json/utc/now'
    url = 'https://worldtimeapi.org/api/timezone/Etc/UTC'
    time_json = requests.get(url).json()
    epoch = time_json['unixtime']
    return epoch


def get_local_epoch():
    epoch_time = int(time.time())
    return epoch_time


def no_receipt_timeout():
    print('No receipts received. Timing out.')


def mine():
    if should_i_mine():
        print('Mining block.')
        run_updater()


def start_receipt_timeout():
    timer = threading.Timer(NO_RECEIPT_COMMITTEE_TIMEOUT, no_receipt_timeout)
    timer.start()


def start_mining_clock():
    mine()
    timer = threading.Timer(BLOCK_TIME_INTERVAL_SECONDS, start_mining_clock)
    timer.start()


def start_miner_broadcast_clock():
    print('Broadcasting miner update')
    broadcast_miner_update()
    timer = threading.Timer(TIME_MINER_BROADCAST_INTERVAL, start_miner_broadcast_clock)
    timer.start()


def get_time_difference():
    """Return the time difference between local and global in seconds"""
    global_epoch = get_global_epoch()
    local_epoch = get_local_epoch()
    return global_epoch - local_epoch


def update_time_difference():
    TIME_DIFF_WITH_GLOBAL = get_time_difference()
    print('Time difference with global is ', TIME_DIFF_WITH_GLOBAL)
    if TIME_DIFF_WITH_GLOBAL > MAX_ALLOWED_TIME_DIFF_SECONDS:
        print('System time is not syncronised. Time difference in seconds: ', TIME_DIFF_WITH_GLOBAL)
        quit()
    return True


if __name__ == '__main__':
    print('Time difference is ', get_time_difference())
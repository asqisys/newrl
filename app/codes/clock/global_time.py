import sys
import time
import requests
import threading
from ...constants import BLOCK_TIME_INTERVAL_SECONDS, MAX_ALLOWED_TIME_DIFF_SECONDS, NO_RECEIPT_COMMITTEE_TIMEOUT, TIME_DIFF_WITH_GLOBAL, TIME_DIFF_WITH_GLOBAL_FILE, TIME_MINER_BROADCAST_INTERVAL


def get_global_epoch():
    # url = 'http://worldclockapi.com/api/json/utc/now'
    url = 'https://worldtimeapi.org/api/timezone/Etc/UTC'
    time_json = requests.get(url).json()
    epoch = time_json['unixtime']
    return epoch


def get_local_epoch():
    epoch_time = int(time.time())
    return epoch_time


def get_time_difference():
    """Return the time difference between local and global in seconds"""
    try:
        with open(TIME_DIFF_WITH_GLOBAL_FILE, 'r') as f:
            return int(f.read())
    except:
        global_epoch = get_global_epoch()
        local_epoch = get_local_epoch()
        diff = global_epoch - local_epoch
        with open(TIME_DIFF_WITH_GLOBAL_FILE, 'w') as f:
            f.write(str(diff))
        return diff


def sync_timer_clock_with_global():
    global_epoch = get_global_epoch()
    local_epoch = get_local_epoch()
    diff = global_epoch - local_epoch
    with open(TIME_DIFF_WITH_GLOBAL_FILE, 'w') as f:
        f.write(str(diff))
    print('Synced clock. Time difference is', diff)


if __name__ == '__main__':
    print('Time difference is ', get_time_difference())
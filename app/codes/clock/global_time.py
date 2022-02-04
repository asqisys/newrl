import requests
import threading
from constants import NO_RECEIPT_COMMITTEE_TIMEOUT


def get_epoch():
    # url = 'http://worldclockapi.com/api/json/utc/now'
    url = 'https://worldtimeapi.org/api/timezone/Etc/UTC'
    time_json = requests.get(url).json()
    epoch = time_json['unixtime']
    return epoch


def no_receipt_timeout():
    print('No receipts received. Timing out.')


def start_receipt_timeout():
    timer = threading.Timer(NO_RECEIPT_COMMITTEE_TIMEOUT, no_receipt_timeout)
    timer.start()
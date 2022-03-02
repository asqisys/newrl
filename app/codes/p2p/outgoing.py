import requests
from threading import Thread
from ...constants import NEWRL_PORT, REQUEST_TIMEOUT, TRANSPORT_SERVER
from ..p2p.utils import get_peers
from ..p2p.utils import is_my_address


def propogate_transaction_to_peers(transaction):
    peers = get_peers()
        
    for peer in peers:
        if is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        print('Broadcasting transaction to peer', url)
        try:
            thread = Thread(target=send_request, args = (url + '/validate-transaction', transaction))
            thread.start()
        except Exception as e:
            print(f'Error broadcasting block to peer: {url}')
            print(e)

def send_request_in_thread(url, data):
    thread = Thread(target=send_request, args = (url, data))
    thread.start()

def send_request(url, data):
    requests.post(url, json=data, timeout=REQUEST_TIMEOUT)

def send(payload):
    response = requests.post(TRANSPORT_SERVER + '/send', json=payload, timeout=REQUEST_TIMEOUT)
    if response.status_code != 200:
        print('Error sending')
    return response.text

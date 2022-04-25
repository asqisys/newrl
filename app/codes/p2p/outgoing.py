import random
import requests
from threading import Thread

from ...constants import IS_TEST, MAX_BROADCAST_NODES, NEWRL_PORT, REQUEST_TIMEOUT, TRANSPORT_SERVER
from ..p2p.utils import get_peers
from ..p2p.utils import is_my_address


def propogate_transaction_to_peers(transaction):
    if IS_TEST:
        return
    peers = get_peers()

    node_count = min(MAX_BROADCAST_NODES, len(peers))
    peers = random.sample(peers, k=node_count)
        
    print('Broadcasting transaction to peers', peers)
    for peer in peers:
        if is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        payload = {'signed_transaction': transaction}
        try:
            thread = Thread(target=send_request, args = (url + '/receive-transaction', payload))
            thread.start()
        except Exception as e:
            print(f'Error broadcasting block to peer: {url}')
            print(e)

def send_request_in_thread(url, data):
    thread = Thread(target=send_request, args = (url, data))
    thread.start()

def send_request(url, data):
    if IS_TEST:
        return
    try:
        requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        print(f'Could not send request to node {url}')

def send(payload):
    response = requests.post(TRANSPORT_SERVER + '/send', json=payload, timeout=REQUEST_TIMEOUT)
    if response.status_code != 200:
        print('Error sending')
    return response.text


def broadcast_receipt(receipt, nodes):
    print('Broadcasting receipt to nodes')
    if IS_TEST:
        return

    for node in nodes:
        if 'network_address' not in node:
            continue
        if is_my_address(node['network_address']):
            continue
        url = 'http://' + node['network_address'] + ':' + str(NEWRL_PORT)
        print('Sending receipt to node', url)
        payload = {'receipt': receipt}
        try:
            thread = Thread(target=send_request, args=(url + '/receive-receipt', payload))
            thread.start()
        except Exception as e:
            print(f'Could not send receipt to node: {url}')


def broadcast_block(block_payload, nodes=None):
    if IS_TEST:
        return
    if nodes:
        peers = []
        for node in nodes:
            if 'network_address' in node:
                peers.append({'address': node['network_address']})
            elif 'address' in node:
                peers.append({'address': node['address']})
        if len(peers) == 0:
            peers = get_peers()
            node_count = min(MAX_BROADCAST_NODES, len(peers))
            peers = random.sample(peers, k=node_count)
    else:
        peers = get_peers()
        node_count = min(MAX_BROADCAST_NODES, len(peers))
        peers = random.sample(peers, k=node_count)

    print('Broadcasting block to peers', peers)

    # TODO - Do not send to self
    for peer in peers:
        if 'address' not in peer or is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        try:
            send_request_in_thread(url + '/receive-block', {'block': block_payload})
            # requests.post(url + '/receive-block', json={'block': block_payload}, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f'Error sending block to peer: {url}')
            print(e)
    return True

import json
import os
import requests
from codes import blockchain
from codes.constants import REQUEST_TIMEOUT
from codes.p2p.peers import get_peers
from codes.updater import update_db_states


def get_blocks(block_indexes):
    blocks = []
    for block_index in block_indexes:
        blocks.append(get_block(block_index))
    return blocks

def receive_block(block):
    print('Recieved block', block)
    blockchain.add_block(block)
    return True
    
def get_block(block_index):
    chain = blockchain.Blockchain()
    return chain.get_block(block_index)

def get_last_block_index():
    last_block = blockchain.get_last_block_index()
    return last_block


def sync_chain_from_node(url):
    their_last_block_index = int(requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT).text)
    my_last_block = get_last_block_index()

    while my_last_block < their_last_block_index:
        my_last_block += 1
        blocks_request = {'transaction_codes': [my_last_block]}
        print(f'Asking block node {url} for block {my_last_block}')
        try:
            blocks_data = requests.post(url + '/get-blocks', json=blocks_request, timeout=REQUEST_TIMEOUT).json()
            for block in blocks_data:
                blockchain.add_block(block)
                break
        except Exception as e:
            print('No more blocks')

        # return my_last_block


def sync_chain_from_peers():
    peers = get_peers()
    url = get_best_peer_to_sync(peers)
    print('Syncing from peer', url)
    sync_chain_from_node(url)


# TODO - use mode of max last 
def get_best_peer_to_sync(peers):
    best_peer = None
    best_peer_value = 0

    for peer in peers:
        url = 'http://' + peer['address'] + ':8092'
        their_last_block_index = int(requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT).text)
        print(f'Peer {url} has last block {their_last_block_index}')
        if their_last_block_index > best_peer_value:
            best_peer = url
            best_peer_value = their_last_block_index
    return best_peer
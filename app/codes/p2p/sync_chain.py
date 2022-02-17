import logging
import json
import os
import requests
import sqlite3

from app.codes import blockchain
from app.constants import NEWRL_PORT, REQUEST_TIMEOUT, NEWRL_DB
from app.codes.p2p.peers import get_peers
from app.codes.updater import update_db_states
from app.codes.validator import validate_block, validate_block_data, validate_receipt_signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_blocks(block_indexes):
    blocks = []
    for block_index in block_indexes:
        blocks.append(get_block(block_index))
    return blocks


def get_block(block_index):
    chain = blockchain.Blockchain()
    return chain.get_block(block_index)

def get_last_block_index():
    last_block = blockchain.get_last_block_index()
    return last_block


def receive_block(block):
    print('Recieved block', block)

    block_index = block['block_index'] if 'block_index' in block else block['index']
    if block_index > get_last_block_index() + 1:
        sync_chain_from_peers()
    
    validate_block(block, validate_receipts=False)
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    blockchain.add_block(cur, block['data'])
    con.close()
    
    return True


def receive_receipt(receipt):
    logger.info('Recieved receipt: %s', receipt)
    if not validate_receipt_signature(receipt):
        logger.info('Invalid receipt signature')
        return False

    # TODO - Add the receipt to an existing block in Temp folder
    #   if no corresponding block exists, store the receipt in temp folder and request  
    #   sender node for the block in receipt

    return True


def sync_chain_from_node(url):
    their_last_block_index = int(requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT).text)
    my_last_block = get_last_block_index() + 1

    print(their_last_block_index, my_last_block)
    # return
    while my_last_block < their_last_block_index:
        blocks_request = {'block_indexes': [my_last_block]}
        print(f'Asking block node {url} for block {my_last_block}')
        try:
            blocks_data = requests.post(url + '/get-blocks', json=blocks_request, timeout=REQUEST_TIMEOUT).json()
        except Exception as e:
            print('Could not get block', str(e))
            my_last_block += 1
            # TODO - Might have to break execution or the chain could be corrupted
            break
        for block in blocks_data:
            if not validate_block_data(block):
                print('Invalid block')
                break
            con = sqlite3.connect(NEWRL_DB)
            cur = con.cursor()
            blockchain.add_block(cur, block)
            con.commit()
            con.close()
        
        my_last_block += 1

    return my_last_block


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
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        try:
            their_last_block_index = int(requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT).text)
            print(f'Peer {url} has last block {their_last_block_index}')
            if their_last_block_index > best_peer_value:
                best_peer = url
                best_peer_value = their_last_block_index
        except Exception as e:
            print('Error getting block index from peer at', url)
    return best_peer
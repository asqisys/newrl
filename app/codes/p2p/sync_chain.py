import json
import logging
import random
import requests
import sqlite3
import time

from app.codes import blockchain
from app.codes.crypto import calculate_hash
from app.codes.minermanager import get_committee_for_current_block
from app.codes.p2p.outgoing import broadcast_receipt
from app.constants import NEWRL_PORT, REQUEST_TIMEOUT, NEWRL_DB
from app.codes.p2p.peers import get_peers

from app.codes.validator import validate_block, validate_block_data, validate_receipt_signature
from app.codes.updater import broadcast_block, start_mining_clock
from app.codes.fs.temp_manager import append_receipt_to_block_in_storage, get_blocks_for_index_from_storage, store_block_to_temp, store_receipt_to_temp
from app.codes.consensus.consensus import check_community_consensus, validate_block_miner, generate_block_receipt, \
    add_my_receipt_to_block

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IS_SYNCING = False

def get_blocks(block_indexes):
    blocks = []
    for block_index in block_indexes:
        block = get_block(block_index)
        if block:
            blocks.append(get_block(block_index))
        else:
            break
    return blocks


def get_block(block_index):
    chain = blockchain.Blockchain()
    return chain.get_block(block_index)

def get_last_block_index():
    last_block = blockchain.get_last_block_index()
    return last_block


def receive_block(block):
    print('Received block', block)

    block_index = block['index']

    if blockchain.block_exists(block_index):
        print('Block alredy exist in chain. Ignoring.')
        return False

    if block_index > get_last_block_index() + 1:
        sync_chain_from_peers()
    
    if not validate_block_miner(block['data']):
        return False

    validate_block(block, validate_receipts=False)

    my_receipt = add_my_receipt_to_block(block)
    if check_community_consensus(block):
        accept_block(block, block['hash'])
        broadcast_block(block)
    else:
        if my_receipt:
            committee = get_committee_for_current_block()
            broadcast_receipt(my_receipt, committee)
        store_block_to_temp(block)
    
    return True


def sync_chain_from_node(url, block_index=None):
    """Update local chain and state from remote node"""
    if block_index is None:
        response = requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT)
        their_last_block_index = int(response.text)
    else:
        their_last_block_index = block_index
    my_last_block = get_last_block_index()
    print(f'I have {my_last_block} blocks. Node {url} has {their_last_block_index} blocks.')

    block_idx = my_last_block + 1
    block_batch_size = 50  # Fetch blocks in batches
    while block_idx <= their_last_block_index:
        failed_for_invalid_block = False
        blocks_to_request = list(range(block_idx, 1 + min(their_last_block_index, block_idx + block_batch_size)))
        blocks_request = {'block_indexes': blocks_to_request}
        print(f'Asking block node {url} for blocks {blocks_request}')
        blocks_data = get_block_from_url_retry(url, blocks_request)
        # try:
        #     response = requests.post(
        #             url + '/get-blocks',
        #             json=blocks_request,
        #             timeout=REQUEST_TIMEOUT
        #         )
        #     blocks_data = response.json()
        # except Exception as err:
        #     print('Could not get block', str(err))
        #     failed_for_invalid_block = True
        #     time.sleep(5)
        for block in blocks_data:
            if not validate_block_data(block):
                print('Invalid block')
                failed_for_invalid_block = True
                break
            con = sqlite3.connect(NEWRL_DB)
            cur = con.cursor()
            for idx, tx in enumerate(block['text']['transactions']):
                specific_data = tx['specific_data']
                while isinstance(specific_data, str):
                    specific_data = json.loads(specific_data)
                block['text']['transactions'][idx]['specific_data'] = json.dumps(specific_data)
            blockchain.add_block(cur, block)
            con.commit()
            con.close()

        if failed_for_invalid_block:
            break

        block_idx += block_batch_size + 1

    return their_last_block_index


def sync_chain_from_peers():
    global IS_SYNCING
    if IS_SYNCING:
        print('Already syncing chain. Not syncing again.')
        return
    IS_SYNCING = True
    peers = get_peers()
    url, block_index = get_best_peer_to_sync(peers)

    if url:
        print('Syncing from peer', url)
        sync_chain_from_node(url, block_index)
    else:
        print('No node available to sync')
    IS_SYNCING = False


# TODO - use mode of max last 
def get_best_peer_to_sync(peers):
    best_peers = []
    best_peer_value = 0

    peers = random.sample(peers, k=min(len(peers), 5))
    for peer in peers:
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        try:
            their_last_block_index = int(requests.get(url + '/get-last-block-index', timeout=REQUEST_TIMEOUT).text)
            print(f'Peer {url} has last block {their_last_block_index}')
            if their_last_block_index > best_peer_value:
                best_peers = [url]
                best_peer_value = their_last_block_index
            elif their_last_block_index == best_peer_value:
                best_peers.append(url)
        except Exception as e:
            print('Error getting block index from peer at', url)
    best_peer = random.choice(best_peers)
    return best_peer, best_peer_value


def ask_peer_for_block(peer_url, block_index):
    blocks_request = {'block_indexes': [block_index]}
    print(f'Asking block node {peer_url} for block {block_index}')
    try:
        blocks_data = requests.post(peer_url + '/get-blocks', json=blocks_request, timeout=REQUEST_TIMEOUT * 5).json()
        return blocks_data
    except Exception as e:
        print('Could not get block', str(e))
        return None


def ask_peers_for_block(block_index):
    peers = get_peers()
    peers = []
    for peer in peers:
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        block = ask_peer_for_block(url, block_index)
        if block is not None:
            return block
    return None


def accept_block(block, hash=None):
    if hash is None:
        hash = calculate_hash(block)
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    blockchain.add_block(cur, block['data'], hash)
    con.commit()
    con.close()

    block_timestamp = int(block['data']['timestamp'])
    start_mining_clock(block_timestamp)


def receive_receipt(receipt):
    logger.info('Recieved receipt: %s', receipt)
    if not validate_receipt_signature(receipt):
        logger.info('Invalid receipt signature')
        return False

    receipt_data = receipt['data']
    block_index = receipt_data['block_index']

    if blockchain.block_exists(block_index):
        return False

    blocks = get_blocks_for_index_from_storage(block_index)
    if len(blocks) == 0:
        store_receipt_to_temp(receipt)
        # block = ask_peers_for_block(block_index)
        # if block is not None:
        #     append_receipt_to_block(block, receipt)
        #     store_block_to_temp(block)
    else:
        blocks_appended = append_receipt_to_block_in_storage(receipt)
        for block in blocks_appended:
            if check_community_consensus(block):
                accept_block(block)
                broadcast_block(block)

    return True


def get_block_from_url_retry(url, blocks_request):
    response = None
    while response is None or response.status_code != 200:
        try:
            response = requests.post(
                    url + '/get-blocks',
                    json=blocks_request,
                    # timeout=REQUEST_TIMEOUT
                )
        except Exception as err:
            print('Retrying block get', str(err))
            failed_for_invalid_block = True
            time.sleep(5)
    blocks_data = response.json()
    return blocks_data
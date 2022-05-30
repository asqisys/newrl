import logging
import requests
import sqlite3
import time

from app.codes import blockchain
from app.constants import NEWRL_PORT, REQUEST_TIMEOUT, NEWRL_DB
from app.codes.p2p.peers import get_peers

from app.codes.validator import validate_block, validate_block_data, validate_receipt_signature
from app.codes.updater import broadcast_block
from app.codes.fs.temp_manager import append_receipt_to_block, append_receipt_to_block_in_storage, get_blocks_for_index_from_storage, store_block_to_temp, store_receipt_to_temp
from app.codes.consensus.consensus import check_community_consensus, validate_block_miner


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
    
    validate_block_miner(block)

    validate_block(block, validate_receipts=False)

    # if check_community_consensus(block):
    #     accept_block(block)
    # else:
    #     store_block_to_temp(block)

    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    blockchain.add_block(cur, block['data'], block['hash'])
    con.commit()
    con.close()
    
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
        blocks_to_request = list(range(block_idx, min(their_last_block_index, block_idx + block_batch_size)))
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
            blockchain.add_block(cur, block)
            con.commit()
            con.close()

        if failed_for_invalid_block:
            break

        block_idx += block_batch_size

    return their_last_block_index


def sync_chain_from_peers():
    peers = get_peers()
    url, block_index = get_best_peer_to_sync(peers)

    if url:
        print('Syncing from peer', url)
        sync_chain_from_node(url, block_index)
    else:
        print('No node available to sync')




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
    return best_peer, best_peer_value


def ask_peer_for_block(peer_url, block_index):
    blocks_request = {'block_indexes': [block_index]}
    print(f'Asking block node {peer_url} for block {block_index}')
    try:
        blocks_data = requests.post(peer_url + '/get-blocks', json=blocks_request, timeout=REQUEST_TIMEOUT).json()
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


def accept_block(block, broadcast=True):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    blockchain.add_block(cur, block)
    con.close()

    broadcast_block(block)


def receive_receipt(receipt):
    logger.info('Recieved receipt: %s', receipt)
    if not validate_receipt_signature(receipt):
        logger.info('Invalid receipt signature')
        return False

    receipt_data = receipt['data']
    block_index = receipt_data['block_index']
    blocks = get_blocks_for_index_from_storage(block_index)
    if len(blocks) == 0:
        store_receipt_to_temp(receipt)
        block = ask_peers_for_block(block_index)
        if block is not None:
            append_receipt_to_block(block, receipt)
            store_block_to_temp(block)
    else:
        blocks_appended = append_receipt_to_block_in_storage(receipt)
        for block in blocks_appended:
            if check_community_consensus(block):
                accept_block(block)
                


    return True


def get_block_from_url_retry(url, blocks_request):
    response = None
    while response is None or response.status_code != 200:
        try:
            response = requests.post(
                    url + '/get-blocks',
                    json=blocks_request,
                    timeout=REQUEST_TIMEOUT
                )
        except Exception as err:
            print('Retrying block get', str(err))
            failed_for_invalid_block = True
            time.sleep(5)
    blocks_data = response.json()
    return blocks_data
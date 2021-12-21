import json
import os
import requests
from codes import blockchain
from codes.updater import update_db_states


def get_blocks(block_indexes):
    blocks = []
    for block_index in block_indexes:
        blocks.append(get_block(block_index))
    return blocks

def get_block(block_index):
    chain = blockchain.Blockchain()
    return chain.get_block(block_index)

def get_last_block_index():
    chain = blockchain.Blockchain()
    last_block = chain.get_last_block_index()
    return last_block


def sync_chain_from_node(url):
    their_last_block_index = int(requests.get(url + '/get-last-block-index').text)
    my_last_block = get_last_block_index()

    while my_last_block <= their_last_block_index:
        my_last_block += 1
        blocks_request = {'transaction_codes': [my_last_block]}
        print(f'Asking block node {url} for block {my_last_block}')
        blocks_data = requests.post(url + '/get-blocks', json=blocks_request).json()
        print(blocks_data)
        for block in blocks_data:
            print(block)
            blockchain.add_block(block)
            break

        return my_last_block

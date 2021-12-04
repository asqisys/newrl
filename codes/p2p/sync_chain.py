import json
import os
from codes import blockchain
from codes.updater import update_db_states


def sync_chain():
    chain = blockchain.Blockchain()
    last_block = chain.get_last_block_index()
    # TODO: Request subsequent blocks from others
    # TODO: Update the state based on the recieved blocks


def processBlock(block):
    # Block validation
    update_db_states(block.transactions)


def update_blockchain(block):
    # Validate block
    for transaction in block.text.transactions:
        pass
        # Validate signatures
        #

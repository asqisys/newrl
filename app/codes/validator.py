"""Python programm to validate transactions, blocks and receipts"""

import base64
import datetime
import json
import logging

import ecdsa
import os

from app.codes.p2p.transport import send
from .blockchain import get_last_block_hash
from .transactionmanager import Transactionmanager
from ..constants import MEMPOOL_PATH


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate(transaction):
    transaction_manager = Transactionmanager()
    transaction_manager.set_transaction_data(transaction)
    economics_valid = transaction_manager.econvalidator()
    signatures_valid = transaction_manager.verifytransigns()
    valid = False
    if economics_valid and signatures_valid:
        msg = "All well"
        valid = True
    if not economics_valid:
        msg = "Economic validation failed"
    if not signatures_valid:
        msg = "Invalid signatures"
    check = {'valid': valid, 'msg': msg}

    if valid:  # Economics and signatures are both valid
        transaction_file = f"{MEMPOOL_PATH}transaction-{transaction_manager.transaction['type']}-{transaction_manager.transaction['trans_code']}.json"
        transaction_manager.save_transaction_to_mempool(transaction_file)

        # Broadcaset transaction
        try:
            payload = {
                'operation': 'send_transaction',
                'data': transaction_manager.get_transaction_complete()
            }
            send(payload)
        except:
            print('Error sending transaction to transport server')

    print(check)
    return check


def validate_signature(data, public_key, signature):
    public_key_bytes = base64.b64decode(public_key)
    sign_trans_bytes = base64.decodebytes(signature.encode('utf-8'))
    vk = ecdsa.VerifyingKey.from_string(
        public_key_bytes, curve=ecdsa.SECP256k1)
    message = json.dumps(data).encode()
    try:
        return vk.verify(sign_trans_bytes, message)
    except:
        return False


def validate_receipt_signature(receipt):
    try:
        return validate_signature(receipt['data'], receipt['public'], receipt['signature'])
    except:
        logger.error('Error validating receipt signature')
        return False


def get_node_trust_score(public_key):
    # TODO - Return the actual trust score of the node by lookup on public_key
    return 1

def validate_block_receipts(block):
    total_receipt_count = 0
    postitive_receipt_count = 0
    for receipt in block['receipts']:
        total_receipt_count += 1

        if not validate_receipt_signature(receipt):
            continue

        if receipt['data']['block_index'] != block['index'] or receipt['data']['block_hash'] != block['hash'] or receipt['data']['vote'] < 1:
            continue

        trust_score = get_node_trust_score(receipt['public'])
        valid_probability = 0 if trust_score < 0 else (trust_score + 2) / 5
            # raise Exception('Invalid receipt signature')

        if receipt['data']['block_index'] != block['index'] or receipt['data']['block_hash'] != block['hash']:
            raise Exception('Invalid receipt data')
        
        if receipt['data']['vote'] == 1:
            postitive_receipt_count += 1
    
    return {
        'total_receipt_count': total_receipt_count,
        'postitive_receipt_count': postitive_receipt_count,
    }


def validate_block(block, validate_receipts=True, should_validate_signature=True):
    if block['hash'][:4] != '0000':
        return False

    if not validate_block_data(block['data']):
        return False

    if should_validate_signature:
        sign_valid = validate_signature(
            data=block['data'],
            public_key=block['signature']['public'],
            signature=block['signature']['msgsign']
        )

        if not sign_valid:
            logger.info('Invalid block signature')
            return False

    if validate_receipts:
        receipts_valid = validate_block_receipts(block)
        if not receipts_valid:
            logger.info('Invalid receipts')
            return False
    
    return True


def validate_block_data(block):
    last_block = get_last_block_hash()

    if not last_block:
        # No local chain. Sync anyway.
        return True

    if last_block['hash'] != block['previous_hash']:
        print('Previous block hash does not match latest block')
        return False
    
    block_index = block['block_index'] if 'block_index' in block else block['index']
    if last_block['index'] != block_index - 1:
        print('New block index is not 1 more than last block index')
        return False
    return True
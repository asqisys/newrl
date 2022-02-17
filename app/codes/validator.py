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
    #blockchain = Blockchain("inginesis.json")
    #	blockchain = Blockchain(options.chainfile)
    #	blockchain = Blockchain();
    #	blockchain.loadfromfile("chain.json");

    ts = str(datetime.datetime.now())
    tm = Transactionmanager()
    tm.set_transaction_data(transaction)
    econ = tm.econvalidator()
    signvalid = tm.verifytransigns()
    valid = 0
    if econ and signvalid:
        #		tm.dumptransaction(options.transfile);
        msg = "All well"
        valid = 1
    if not econ:
        msg = "Economic validation failed"
    if not signvalid:
        msg = "Invalid signatures"
    check = {'valid': valid, 'msg': msg}

    checkfile = MEMPOOL_PATH+tm.transaction['trans_code'] + \
        "_validation"+str("-"+ts[0:10]+"-"+ts[-6:]+".json")
    with open(checkfile, "w") as ckfile:
        json.dump(check, ckfile)

    if valid == 1:  # econ and signvalid are both True
        transoutputfile = MEMPOOL_PATH + "transaction-" + \
            str(tm.transaction['type']) + "-" + \
            tm.transaction['trans_code'] + ".json"
        tm.dumptransaction(transoutputfile)
        payload = {
            'operation': 'send_transaction',
            'data': tm.get_transaction()
        }
        # Send to transport server
        try:
            send(payload)
        except:
            print('Error sending transaction to transport server')

    status = f"Wrote check status as {check} to {checkfile}"
    print(status)
    return status


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
        return validate_signature(receipt['data'], receipt['public_key'], receipt['signature'])
    except:
        logger.error('Error validating receipt signature')
        return False


def get_node_trust_score(public_key):
    # TODO - Return the actual trust score of the node by lookup on public_key
    return 1

def validate_block_using_receipts(block):
    total_receipt_count = 0
    score_weighted_validity_count = 0

    for receipt in block['receipts']:
        total_receipt_count += 1

        if not validate_receipt_signature(receipt):
            continue

        if receipt['data']['block_index'] != block['index'] or receipt['data']['block_hash'] != block['hash'] or receipt['data']['vote'] < 1:
            continue

        trust_score = get_node_trust_score(receipt['public_key'])
        valid_probability = 0 if trust_score < 0 else (trust_score + 2) / 5

        score_weighted_validity_count += valid_probability

    if score_weighted_validity_count < 0.75:
        return False
    
    return True


def validate_block(block, validate_receipts=True, should_validate_signature=True):
    block_data = block['data']

    if block['hash'][:4] != '0000':
        return False
    
    last_block = get_last_block_hash()

    if last_block['index'] != block['block_index'] - 1:
        return False
    if last_block and last_block['hash'] != block_data['previous_hash']:
        return False

    if should_validate_signature:
        sign_valid = validate_signature(
            data=block['data'],
            public_key=block['signature']['public_key'],
            signature=block['signature']['msgsign']
        )

        if not sign_valid:
            logger.info('Invalid block signature')
            return False

    if validate_receipts:
        receipts_valid = validate_block_using_receipts(block)
        if not receipts_valid:
            logger.info('Invalid receipts')
            return False
    
    return True

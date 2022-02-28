"""Miner update functions"""
import sqlite3
import random

from .blockchain import get_last_block_hash
from .p2p.utils import get_my_address
from ..constants import COMMITTEE_SIZE, NEWRL_DB
from .auth.auth import get_wallet
from .signmanager import sign_transaction
from ..ntypes import TRANSACTION_MINER_ADDITION
from .utils import get_time_ms
from .transactionmanager import Transactionmanager
from .validator import validate


def miner_addition_transaction():
    wallet = get_wallet()
    my_address = get_my_address()
    timestamp = get_time_ms()
    transaction_data = {
        'timestamp': timestamp,
        'type': TRANSACTION_MINER_ADDITION,
        'currency': "NWRL",
        'fee': 0.0,
        'descr': "Miner addition",
        'valid': 1,
        'block_index': 0,
        'specific_data': {
            'wallet_address': wallet['address'],
            'network_address': my_address,
            'broadcast_timestamp': timestamp
        }
    }

    transaction_manager = Transactionmanager()
    transaction_data = {'transaction': transaction_data, 'signatures': []}
    transaction_manager.transactioncreator(transaction_data)
    transaction = transaction_manager.get_transaction_complete()
    signed_transaction = sign_transaction(wallet, transaction)
    return signed_transaction


def get_miner_status(wallet_address):
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    miner_cursor = cur.execute(
        'SELECT wallet_address, network_address, last_broadcast_timestamp FROM miners WHERE wallet_address=?', (wallet_address, )).fetchone()
    if miner_cursor is None:
        return None
    miner_info = {
        'wallet_address': miner_cursor[0],
        'network_address': miner_cursor[1],
        'broadcast_timestamp': miner_cursor[2]
    }
    return miner_info


def get_my_miner_status():
    wallet = get_wallet()
    my_status = get_miner_status(wallet['address'])
    return my_status


def broadcast_miner_update():
    transaction = miner_addition_transaction()
    validate(transaction)


def get_miner_list():
    con = sqlite3.connect(NEWRL_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    miner_cursor = cur.execute(
        'SELECT wallet_address, network_address, last_broadcast_timestamp FROM miners ORDER BY wallet_address ASC').fetchall()
    miners = [dict(m) for m in miner_cursor]
    return miners


def get_miner_for_current_block():
    last_block = get_last_block_hash()

    if not last_block:
        return

    # TODO - Use hash instead of index
    # random.seed takes integer arguments; hash need to convert to int
    random.seed(last_block['index'])

    miners = get_miner_list()
    miner = random.choice(miners)
    return miner


def get_committee_for_current_block():
    last_block = get_last_block_hash()

    if not last_block:
        return

    random.seed(last_block['index'])

    miners = get_miner_list()
    committee = random.choices(miners, k=COMMITTEE_SIZE)
    return committee


def should_i_mine():
    my_wallet = get_wallet()
    miner = get_miner_for_current_block()
    if miner['wallet_address'] == my_wallet['address']:
        return True
    return False
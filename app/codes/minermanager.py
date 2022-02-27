"""Miner update functions"""
import datetime

from .auth.auth import get_wallet
from .signmanager import sign_transaction
from ..types import TRANSACTION_MINER_ADDITION
from .utils import get_time_ms
from .transactionmanager import Transactionmanager


def miner_addition_transaction():
    transaction_data = {
        'timestamp': get_time_ms(),
        'type': TRANSACTION_MINER_ADDITION,
        'currency': "NWRL",
        'fee': 0.0,
        'descr': "Miner addition",
        'valid': 1,
        'block_index': 0,
        'specific_data': {}
    }

    transaction = Transactionmanager()
    transaction_data = {'transaction': transaction_data, 'signatures': []}
    transaction.transactioncreator(transaction_data)
    wallet = get_wallet()
    signed_transaction = sign_transaction(wallet, transaction_data)
    return signed_transaction

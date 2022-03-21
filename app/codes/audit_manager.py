"""Audit transactions related functions"""
from .auth.auth import get_wallet
from .signmanager import sign_transaction
from ..ntypes import TRANSACTION_AUDIT
from .utils import get_time_ms
from .transactionmanager import Transactionmanager

def audit_transaction(auditparams, wallet=None):
    if wallet is None:
        wallet = get_wallet()
    timestamp = get_time_ms()
    # audit_type can be "transaction","token","person","contract"; person can include DAOs
    # audited_entity is the id of whatever is referred to in audit_type
    # audit_output is 1 for valid, -1 for invalid and 0 for indeterminate
    # doc_hashes are optional list of hashes of documents supporting the output
    transaction_data = {
        'timestamp': timestamp,
        'type': TRANSACTION_AUDIT,
        'currency': "NWRL",
        'fee': 0.0,
        'descr': "Miner addition",
        'valid': 1,
        'block_index': 0,
        'specific_data': {
            'auditor_address': wallet['address'],
            'audit_time': auditparams['audit_time'],
            'audit_type':auditparams['audit_type'],
            'audited_entity':auditparams['audited_entity'],
            'audit_output':auditparams['audit_output'],
            'doc_hashes':auditparams['doc_hashes']
        }
    }

    transaction_manager = Transactionmanager()
    transaction_data = {'transaction': transaction_data, 'signatures': []}
    transaction_manager.transactioncreator(transaction_data)
    transaction = transaction_manager.get_transaction_complete()
    signed_transaction = sign_transaction(wallet, transaction)
    return signed_transaction

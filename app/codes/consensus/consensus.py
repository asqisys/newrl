"""Consensus related functions"""

from ..p2p.peers import get_auth
from ..signmanager import sign_object
from ..blockchain import calculate_hash


auth_data = get_auth()
public_key = auth_data['wallet']['public']
private_key = auth_data['wallet']['private']

def generate_block_receipt(block):
    receipt_data = {
        'block_index': block['index'],
        'block_hash': calculate_hash(block),
        'vote': 1
    }
    return {
        "data": receipt_data,
        "public_key": public_key,
        "signature": sign_object(private_key, receipt_data)
    }

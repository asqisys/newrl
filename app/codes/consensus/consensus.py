"""Consensus related functions"""

from ..signmanager import sign_object
from ..blockchain import calculate_hash
from ..validator import validate_block_receipts
from ..fs.mempool_manager import append_receipt_to_block, get_receipts_from_storage
from ...constants import MINIMUM_ACCEPTANCE_RATIO, MINIMUM_ACCEPTANCE_VOTES
from ..auth.auth import get_wallet


def generate_block_receipt(block):
    receipt_data = {
        'block_index': block['index'],
        'block_hash': calculate_hash(block),
        'vote': 1
    }

    try:
        wallet_data = get_wallet()
    except:
        wallet_data = {
            'wallet': {'public': '', 'private': ''},
        }
    public_key = wallet_data['public']
    private_key = wallet_data['private']
    return {
        "data": receipt_data,
        "public_key": public_key,
        "signature": sign_object(private_key, receipt_data)
    }


def get_node_trust_score(public_key):
    # TODO - Return the actual trust score of the node by lookup on public_key
    return 1

# Probability version
# def check_community_consensus(block):
#     total_receipt_count = 0
#     score_weighted_validity_count = 0

#     for receipt in block['receipts']:
#         total_receipt_count += 1

#         trust_score = get_node_trust_score(receipt['public_key'])
#         valid_probability = 0 if trust_score < 0 else (trust_score + 2) / 5

#         score_weighted_validity_count += valid_probability

#     if score_weighted_validity_count < 0.75:
#         return False
    
#     return True

def check_community_consensus(block):
    receipt_counts = validate_block_receipts(block)
    receipts_in_temp = get_receipts_from_storage(block['index'])
    
    for receipt in receipts_in_temp:
        append_receipt_to_block(block, receipt)
    
    if receipt_counts['postitive_receipt_count'] / receipt_counts['total_receipt_count'] > MINIMUM_ACCEPTANCE_RATIO:
        return True
    
    # if receipt_counts['postitive_receipt_count'] >= MINIMUM_ACCEPTANCE_VOTES and receipt_counts['total_receipt_count']:
    #     return True
    return False
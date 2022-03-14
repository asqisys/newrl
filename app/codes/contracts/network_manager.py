# program for network manager smart contract
from calendar import c
from cmath import log
from app.codes.p2p.sync_chain import get_block
from app.codes.validator import get_node_trust_score
from ..db_updater import *
from ...constants import COMMITTEE_SIZE
from ...nvalues import NW_MANAGER_PID

def update_score_from_receipt(receipt, DELTA):
    receipt['data']['block_index']
    receipt['data']['vote']
    receipt['data']['block_hash']
    nw_trust_score = get_node_trust_score(receipt['public'])
    if not nw_trust_score:
        nw_trust_score = 0.0
    actual_block = get_block(receipt['data']['block_index'])
    if actual_block['hash'] == receipt['data']['block_hash']:   #voted-on block was included
        if receipt['data']['vote'] == 1:    # honest node voted 1 for a valid block
            nw_trust_score = nw_trust_score + DELTA/COMMITTEE_SIZE*log(10.0 - 3*nw_trust_score)
        if receipt['data']['vote'] == -1:   # dishonest node voted -1 for a valid block
            nw_trust_score = nw_trust_score - 5*DELTA/COMMITTEE_SIZE * (3+3*nw_trust_score)
    else:   # voted-on block was not included
        if len(actual_block['transactions']) > 0:  #not an empty block
            if receipt['data']['vote'] == -1:  # honest node voted -1 for an invalid non-empty block
                nw_trust_score = nw_trust_score + DELTA/COMMITTEE_SIZE*log(10.0 - 3*nw_trust_score)
            if receipt['data']['vote'] == 1:   # dishonest node voted 1 for an invalid non-empty block
                nw_trust_score = nw_trust_score - 5*DELTA/COMMITTEE_SIZE * (3+3*nw_trust_score)
    return nw_trust_score

def update_score_for_miner(block):
    pass

def update_network_trust_score(cur, receipts):
    network_size = 100  #need to get the actual size of network using node table in db
    DELTA = 0.1 / log(network_size)
    for receipt in receipts:
        new_score = update_score_from_receipt(receipt, DELTA)
        address = get_address_from_public(receipt['public']) #need to write this in db_updater or utils
        personid = get_person_id_for_wallet_address(address)
        update_trust_score(cur, NW_MANAGER_PID, personid, new_score, get_time_ms())

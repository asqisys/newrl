"""Updater that adds a new block and updates state db"""
import datetime
import json
import os
import sqlite3
import threading

from .clock.global_time import get_corrected_time_ms, get_time_difference
from .fs.temp_manager import get_blocks_for_index_from_storage, store_block_to_temp
from .minermanager import am_i_in_current_committee, broadcast_miner_update, get_committee_for_current_block, get_miner_for_current_block, should_i_mine
from ..nvalues import TREASURY_WALLET_ADDRESS
from ..constants import ALLOWED_FEE_PAYMENT_TOKENS, BLOCK_RECEIVE_TIMEOUT_SECONDS, BLOCK_TIME_INTERVAL_SECONDS, COMMITTEE_SIZE, GLOBAL_INTERNAL_CLOCK_SECONDS, IS_TEST, NEWRL_DB, NEWRL_PORT, NO_BLOCK_TIMEOUT, NO_RECEIPT_COMMITTEE_TIMEOUT, REQUEST_TIMEOUT, MEMPOOL_PATH, TIME_BETWEEN_BLOCKS_SECONDS, TIME_MINER_BROADCAST_INTERVAL_SECONDS
from .p2p.peers import get_peers
from .p2p.utils import is_my_address
from .utils import BufferedLog, get_time_ms
from .blockchain import Blockchain, get_last_block_hash, get_last_block_index
from .transactionmanager import Transactionmanager, get_valid_addresses
from .state_updater import update_db_states
from .crypto import calculate_hash, sign_object, _private, _public
from .consensus.consensus import generate_block_receipt
from .chainscanner import get_wallet_token_balance
from .db_updater import transfer_tokens_and_update_balances
from .p2p.outgoing import broadcast_receipt, send_request_in_thread
from .auth.auth import get_wallet


MAX_BLOCK_SIZE = 1000

TIMERS = {
    'mining_timer': None,
    'block_receive_timeout': None,
}


def run_updater(add_to_chain=False):
    logger = BufferedLog()
    blockchain = Blockchain()

    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    block_time_limit = 1  # Number of hours of no transactions still prompting new block
    block_height = 0
    latest_ts = blockchain.get_latest_ts(cur)

    filenames = os.listdir(MEMPOOL_PATH)  # this is the mempool
    logger.log("Files in mempool: ", filenames)
    textarray = []
    transfiles = filenames
    txcodes = []
    tmtemp = Transactionmanager()

    transaction_fees = 0

    for filename in transfiles:
        file = MEMPOOL_PATH + filename
        try:
            with open(file, "r") as read_file:
                logger.log("Processing ", file)
                transaction_file_data = json.load(read_file)
        except:
            logger.log("Couldn't load transaction file ", file)
            continue
        
        transaction = transaction_file_data['transaction']
        signatures = transaction_file_data['signatures']

        # new code for validating again
        trandata = tmtemp.loadtransactionpassive(file)
        if not tmtemp.verifytransigns():
            logger.log(
                f"Transaction id {trandata['transaction']['trans_code']} has invalid signatures")
            os.remove(file)
            continue
        # Pay fee for transaction. If payee doesn't have enough funds, remove transaction
        if not pay_fee_for_transaction(cur, transaction):
            os.remove(file)
            continue
        if not tmtemp.econvalidator():
            logger.log("Economic validation failed for transaction ",
                        trandata['transaction']['trans_code'])
            os.remove(file)
            continue

        logger.log("Found valid transaction, checking if it is already included")
        transactions_cursor = cur.execute("SELECT * FROM transactions where transaction_code='" + transaction['trans_code'] + "'")
        row = transactions_cursor.fetchone()
        if row is not None:
            # The current transaction is already included in some earlier block
            os.remove(file)
            continue
        
        if not should_include_transaction(transaction):
            os.remove(file)
            continue
        
        if trandata['transaction']['trans_code'] not in txcodes:
            textarray.append(transaction_file_data)
            txcodes.append(trandata['transaction']['trans_code'])

            transaction_fees += get_fees_for_transaction(trandata['transaction'])
            # Delete the transaction from mempool at the stage of accepting
            # try:
            #     os.remove(file)
            # except:
            #     logger.log("Couldn't delete:",file)
        block_height += 1
        if block_height >= MAX_BLOCK_SIZE:
            logger.log(
                "Reached max block height, moving forward with the collected transactions")
            break

    transactionsdata = {"transactions": textarray}
    if len(textarray) > 0:
        logger.log(f"Found {len(textarray)} transactions. Adding to chain")
    else:
        logger.log("No new transactions. Checking for time.")
        logger.log("latest ts:", latest_ts, "\tNow: ", datetime.datetime.now())
        try:
            time_diff = get_time_ms() - int(latest_ts)
        except Exception as e:
            time_diff = TIME_BETWEEN_BLOCKS_SECONDS * 1000 + 1  # Set a high timelimit as no last block timestamp found
        logger.log("Time since last block: ", time_diff, " seconds")
        if time_diff < TIME_BETWEEN_BLOCKS_SECONDS * 1000:  # TODO - Change the block time limit
            logger.log("No new transactions, not enough time since last block. Exiting.")
            return logger.get_logs()
        else:
            logger.log(f"More than {TIME_BETWEEN_BLOCKS_SECONDS} seconds since the last block. Adding a new empty one.")

    print(transactionsdata)
    if add_to_chain:
        block = blockchain.mine_block(cur, transactionsdata)
        update_db_states(cur, block)
        con.commit()
        con.close()
    else:
        block = blockchain.propose_block(cur, transactionsdata)
    block_receipt = generate_block_receipt(block)
    block_payload = {
        'index': block['index'],
        'hash': calculate_hash(block),
        'data': block,
        'receipts': [block_receipt]
    }
    store_block_to_temp(block_payload)
    print('Stored block to temp with payload', json.dumps(block_payload))
    if not IS_TEST:
        nodes = get_committee_for_current_block()
        if len(nodes) < COMMITTEE_SIZE:
            nodes = get_peers()
        broadcast_block(block_payload, nodes)

    return block_payload


def broadcast_block(block_payload, nodes=None):
    if IS_TEST:
        return
    if nodes:
        peers = []
        for node in nodes:
            if 'network_address' in node:
                peers.append({'address': node['network_address']})
            elif 'address' in node:
                peers.append({'address': node['address']})
        if len(peers) == 0:
            peers = get_peers()
    else:
        peers = get_peers()

    print('Broadcasting block to nodes', nodes)

    # TODO - Do not send to self
    for peer in peers:
        if 'address' not in peer or is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        print('Sending block to peer', url)
        try:
            send_request_in_thread(url + '/receive-block', {'block': block_payload})
            # requests.post(url + '/receive-block', json={'block': block_payload}, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f'Error sending block to peer: {url}')
            print(e)
    return True


def get_fees_for_transaction(transaction):
    return transaction['fee']


def pay_fee_for_transaction(cur, transaction):
    fee = get_fees_for_transaction(transaction)

    # Check for 0 fee transactions and deprioritize accordingly
    if fee == 0:
        return True

    currency = transaction['currency']
    if currency not in ALLOWED_FEE_PAYMENT_TOKENS:
        return False

    payees = get_valid_addresses(transaction)

    for payee in payees:
        balance = get_wallet_token_balance(payee, currency)
        if balance < fee / len(payees):
            return False
        transfer_tokens_and_update_balances(
            cur,
            payee,
            TREASURY_WALLET_ADDRESS,
            transaction['currency'],
            fee / len(payees)
        )
    return True


def create_empty_block_receipt_and_broadcast():
    block_index = get_last_block_index() + 1
    print('No block timeout. Mining empty block')
    blocks_in_storage = get_blocks_for_index_from_storage(block_index)
    if len(blocks_in_storage) != 0:
        print('Block already exist in storage. Not mining empty block.')
        return
    blockchain = Blockchain()
    block = blockchain.mine_empty_block()
    block_receipt = generate_block_receipt(block)
    block_payload = {
        'index': block['index'],
        'hash': calculate_hash(block),
        'data': block,
        'receipts': [block_receipt]
    }
    store_block_to_temp(block_payload)

    committee = get_committee_for_current_block()
    broadcast_receipt(block_receipt, committee)


def start_empty_block_mining_clock():
    global TIMERS
    if TIMERS['block_receive_timeout'] is not None:
        TIMERS['block_receive_timeout'].cancel()
    timer = threading.Timer(NO_BLOCK_TIMEOUT + BLOCK_TIME_INTERVAL_SECONDS, create_empty_block_receipt_and_broadcast)
    timer.start()
    TIMERS['block_receive_timeout'] = timer


def mine(add_to_chain=False):
    if should_i_mine() or add_to_chain:
        print('I am the miner for this block.')
        return run_updater(add_to_chain)
    # elif am_i_in_current_committee():
    #     start_empty_block_mining_clock()
    #     print('I am committee member. Starting no block timeout.')
    else:
        miner = get_miner_for_current_block()
        print(f"Miner for current block is {miner['wallet_address']}. Waiting to receive block.")


def start_mining_clock(block_timestamp):
    global TIMERS
    if TIMERS['mining_timer'] is not None:
        TIMERS['mining_timer'].cancel()
    if TIMERS['block_receive_timeout'] is not None:
        TIMERS['block_receive_timeout'].cancel()
        TIMERS['block_receive_timeout'] = None
    current_ts_seconds = get_corrected_time_ms() / 1000
    block_ts_seconds = block_timestamp / 1000
    seconds_to_wait = block_ts_seconds + BLOCK_TIME_INTERVAL_SECONDS - current_ts_seconds
    print(f'Block time timestamp is {block_ts_seconds}. Current timestamp is {current_ts_seconds}. Waiting {seconds_to_wait} seconds to mine next block')
    timer = threading.Timer(seconds_to_wait, mine)
    timer.start()
    TIMERS['mining_timer'] = timer


def start_miner_broadcast_clock():
    print('Broadcasting miner update')
    try:
        broadcast_miner_update()
    except Exception as e:
        print('Could not broadcast miner update', str(e))
    timer = threading.Timer(TIME_MINER_BROADCAST_INTERVAL_SECONDS, start_miner_broadcast_clock)
    timer.start()


def should_include_transaction(transaction):
    if transaction['type'] == 7:
        broadcast_timestamp = transaction['specific_data']['broadcast_timestamp']
        if broadcast_timestamp < get_corrected_time_ms() - TIME_MINER_BROADCAST_INTERVAL_SECONDS * 1000:
            return False
    return True


def global_internal_clock():
    """Reccuring clock for all node level activities"""
    
    try:
        # Check for mining delay
        current_ts = get_corrected_time_ms()
        last_block = get_last_block_hash()
        if last_block:
            last_block_ts = int(last_block['timestamp'])
            time_elapsed_seconds = (current_ts - last_block_ts) / 1000

            if time_elapsed_seconds > BLOCK_TIME_INTERVAL_SECONDS * 3:
                start_mining_clock(last_block_ts)
                start_empty_block_mining_clock()
    except Exception as e:
        print('Error in global clock', e)

    timer = threading.Timer(GLOBAL_INTERNAL_CLOCK_SECONDS, global_internal_clock)
    timer.start()
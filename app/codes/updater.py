"""Updater that adds a new block and updates state db"""
import datetime
import json
import os
import sqlite3
import threading
import requests

from .clock.global_time import get_time_difference
from .minermanager import am_i_in_current_committee, broadcast_miner_update, get_miner_for_current_block, should_i_mine
from ..nvalues import TREASURY_WALLET_ADDRESS
from ..constants import ALLOWED_FEE_PAYMENT_TOKENS, BLOCK_RECEIVE_TIMEOUT_SECONDS, BLOCK_TIME_INTERVAL_SECONDS, IS_TEST, NEWRL_DB, NEWRL_PORT, NO_RECEIPT_COMMITTEE_TIMEOUT, REQUEST_TIMEOUT, MEMPOOL_PATH, TIME_BETWEEN_BLOCKS_SECONDS, TIME_MINER_BROADCAST_INTERVAL
from .p2p.peers import get_peers, remove_peer
from .p2p.utils import is_my_address
from .utils import BufferedLog, get_time_ms
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager, get_valid_addresses
from .state_updater import update_db_states
from .crypto import calculate_hash, sign_object, _private, _public
from .consensus.consensus import generate_block_receipt
from .chainscanner import get_wallet_token_balance
from .db_updater import transfer_tokens_and_update_balances
from .p2p.outgoing import send_request_in_thread
from .auth.auth import get_wallet


MAX_BLOCK_SIZE = 10

def run_updater():
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
    signarray = []
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
        
        if trandata['transaction']['trans_code'] not in txcodes:
            textarray.append(transaction)
            signarray.append(signatures)
            txcodes.append(trandata['transaction']['trans_code'])

            transaction_fees += get_fees_for_transaction(trandata['transaction'])
            try:
                os.remove(file)
            except:
                logger.log("Couldn't delete:",file)
        block_height += 1
        if block_height >= MAX_BLOCK_SIZE:
            logger.log(
                "Reached max block height, moving forward with the collected transactions")
            break

    transactionsdata = {"transactions": textarray, "signatures": signarray}
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
    block = blockchain.mine_block(cur, transactionsdata, transaction_fees)
    update_db_states(cur, block)
    con.commit()
    con.close()

    # Generate and add a single receipt to the block of mining node
    # block_receipt = generate_block_receipt(block)
    # block['receipts'] = [block_receipt]

    if not IS_TEST:
        broadcast_block(block)

    return logger.get_logs()

def broadcast_block(block):
    peers = get_peers()

    my_wallet = get_wallet()
    private_key = my_wallet['private']
    public_key = my_wallet['public']
    address = my_wallet['address']
    signature = {
        'address': address,
        'public': public_key,
        'msgsign': sign_object(private_key, block)
    } 
    block_payload = {
        'block_index': block['index'],
        'hash': calculate_hash(block),
        'data': block,
        'signature': signature
    }

    print(json.dumps(block_payload))

    # TODO - Do not send to self
    for peer in peers:
        if is_my_address(peer['address']):
            continue
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        print('Broadcasting to peer', url)
        try:
            send_request_in_thread(url + '/receive-block', {'block': block_payload})
            # requests.post(url + '/receive-block', json={'block': block_payload}, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f'Error broadcasting block to peer: {url}')
            print(f'Delete peer {peer}')
            remove_peer(peer)
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


def mine_empty_block():
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    blockchain = Blockchain()

    block = blockchain.mine_empty_block(cur, {'transactions': []})
    # update_db_states(cur, block)

    con.commit()
    con.close()

    return block


def no_receipt_timeout():
    print('Inadequate receipts. Timing out and sending empty block.')


def mine():
    if should_i_mine():
        print('I am the miner for this block.')
        run_updater()
    else:
        miner = get_miner_for_current_block()
        print(f"Miner for current block is {miner['wallet_address']}. Waiting to receive block.")
        start_block_receive_timeout_clock()

def start_receipt_timeout():
    timer = threading.Timer(NO_RECEIPT_COMMITTEE_TIMEOUT, no_receipt_timeout)
    timer.start()


def start_mining_clock():
    mine()
    timer = threading.Timer(BLOCK_TIME_INTERVAL_SECONDS, start_mining_clock)
    timer.start()


def block_receive_timeout():
    miner = get_miner_for_current_block()
    print(f"Block receive timed out from miner {miner['wallet_address']}")
    block_index = mine_empty_block()['index']
    print(f"Mined new block {block_index}")


def start_block_receive_timeout_clock():
    timer = threading.Timer(BLOCK_RECEIVE_TIMEOUT_SECONDS, block_receive_timeout)
    timer.start()


def start_miner_broadcast_clock():
    print('Broadcasting miner update')
    broadcast_miner_update()
    timer = threading.Timer(TIME_MINER_BROADCAST_INTERVAL, start_miner_broadcast_clock)
    timer.start()


def start_timers(block_timestamp):
    print('Starting timer with timestamp ', block_timestamp)

    my_global_timestamp = get_time_ms() - get_time_difference()
    propogation_delay = my_global_timestamp - block_timestamp

    # If I'm miner, start mining clock
    if should_i_mine():
        wait_time =  BLOCK_TIME_INTERVAL_SECONDS - propogation_delay
        timer = threading.Timer(wait_time, mine)
        timer.start()
    elif am_i_in_current_committee():
        wait_time = NO_RECEIPT_COMMITTEE_TIMEOUT - propogation_delay
        timer = threading.Timer(wait_time, block_receive_timeout)
        timer.start()
    else:
        pass
        # Not a miner and part of committee. No action to be performed
        # Hoping the sentinel node will trigger an empty block start stagnant network
"""Updater that adds a new block and updates state db"""
import datetime
import json
import os
import sqlite3
from nvalues import TREASURY_WALLET_ADDRESS
import requests

from ..constants import ALLOWED_FEE_PAYMENT_TOKENS, IS_TEST, NEWRL_DB, NEWRL_PORT, REQUEST_TIMEOUT, MEMPOOL_PATH, TIME_BETWEEN_BLOCKS_SECONDS
from .p2p.peers import get_peers
from .utils import BufferedLog, get_time_ms
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager, get_valid_addresses
from .state_updater import update_db_states
from .crypto import calculate_hash, sign_object, _private, _public
from .consensus.consensus import generate_block_receipt
from .chainscanner import get_wallet_token_balance
from .db_updater import transfer_tokens_and_update_balances


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
        # if not pay_fee_for_transaction(cur, transaction):
        #     os.remove(file)
        #     continue
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

    private_key = _private
    public_key = _public
    signature = {
        'publicKey': public_key,
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
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        print('Broadcasting to peer', url)
        try:
            requests.post(url + '/receive-block', json={'block': block_payload}, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f'Error broadcasting block to peer: {url}')
            print(e)
    return True


def get_fees_for_transaction(transaction):
    return 1

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

#updater that adds a new block and updates state db

import datetime
import time
import json
from multiprocessing.dummy import current_process
import os
import shutil
import hashlib

import requests
import sqlite3

from ..constants import NEWRL_DB, NEWRL_PORT, REQUEST_TIMEOUT, STATE_FILE, CHAIN_FILE, MEMPOOL_PATH
from .p2p.peers import get_peers
from .utils import BufferedLog
from .blockchain import Blockchain
from .transactionmanager import Transactionmanager
from .chainscanner import Chainscanner, get_wallet_token_balance
from .state_updater import update_db_states
from .crypto import calculate_hash, sign_object, _private, _public

def chainmatch(chain1, chain2):
    len1 = len(chain1)
    len2 = len(chain2)
    commonlen = min(len1, len2)
    index = 1
    while index < commonlen+1:
        blockdata1 = chain1[index-1]
        blockdata2 = chain2[index-1]
        index += 1
        if not blockdata1['previous_hash'] == blockdata2['previous_hash']:
            return False
        if not blockdata1['proof'] == blockdata2['proof']:
            return False
    return True

# def main():


def run_updater():
    logger = BufferedLog()
    blockchain = Blockchain()

    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    max_block_height = 10
    block_time_limit = 1  # number of hours of no transactions still prompting new block
    block_height = 0
    latest_ts = blockchain.get_latest_ts(cur)

    mempool = MEMPOOL_PATH
    # incltrans = options.itpool
    filenames = os.listdir(mempool)  # this is the mempool
    logger.log("Files in mempool: ", filenames)
    textarray = []
    signarray = []
    transfiles = []
    validationfiles = []
    txcodes = []
    tmtemp = Transactionmanager()
    for filename in filenames:
        if "validation" in filename:  # the validation files
            validationfiles.append(filename)
        if "transaction" in filename:
            transfiles.append(filename)

    for filename in transfiles:
        file = mempool+filename
    #	if "validation" in file:	#the validation files
    #		continue
        if ".json" in file:
            try:
                with open(file, "r") as read_file:
                    logger.log("processing ", file)
                    transactiondata = json.load(read_file)
            except:
                logger.log("Couldn't load transaction file ", file)
                continue
            transaction = transactiondata['transaction']
            signatures = transactiondata['signatures']

            # new code for validating again
            trandata = tmtemp.loadtransactionpassive(file)
            if not tmtemp.verifytransigns():
                logger.log(
                    "Transaction id ", trandata['transaction']['trans_code'], " has invalid signatures")
                continue
            if not tmtemp.econvalidator():
                logger.log("Economic validation failed for transaction ",
                           trandata['transaction']['trans_code'])
                continue
            # end new code
            trancodestr = trandata['transaction']['trans_code']
            totalchecks = 0
            validchecks = 0
            specificvalfiles = []
            for flname in validationfiles:
                if trancodestr in flname:
                    validationfile = mempool+flname
                    # to enable easy move out later from mempool
                    specificvalfiles.append(validationfile)
                    try:
                        with open(validationfile, "r") as read_file:
                            validitydata = json.load(read_file)
                        totalchecks += 1  # all checks including those that rejected
                        if validitydata['valid'] == 1:
                            validchecks += 1  # only the successful checks
                    except:
                        logger.log(
                            "could not load validity data from ", validationfile)
            tranvalidity = 0
            if totalchecks < 1:
                tranvalidity = 0
            else:
                logger.log("Proportion of valid checks = ",
                           float(validchecks/totalchecks))
                if float(validchecks/totalchecks) > 0.5:  # majority
                    tranvalidity = 1

            traninclusionflag = False
            if tranvalidity == 1:
                #	logger.log("Found valid transaction, adding to block. Moving file to ",incltrans)
                logger.log(
                    "Found valid transaction, checking if it is already included")
                transactions_cursor = cur.execute("SELECT * FROM transactions where transaction_code='" + transaction['trans_code'] + "'")
                row = transactions_cursor.fetchone()
                if row is not None:
                    traninclusionflag = True
                    continue
                if traninclusionflag:  # the current transaction is already included in some earlier block
                    continue  # this takes the process to the next transaction
                
                if trandata['transaction']['trans_code'] not in txcodes:
                    textarray.append(transaction)
                    signarray.append(signatures)
                    txcodes.append(trandata['transaction']['trans_code'])
                    try:
                        os.remove(file)
                    	# shutil.move(file, incltrans);
                    except:
                    	logger.log("Couldn't delete:",file)
                # for vfile in specificvalfiles:
                # 	try:
                # 		shutil.move(vfile, options.itpool)
                # 	except:
                # 		logger.log("couldn't move ",vfile)
                block_height += 1
                if block_height >= max_block_height:
                    logger.log(
                        "Reached max block height, moving forward with the collected transactions")
                    break
            else:
                logger.log(
                    "Did not find valid transaction, not adding to block")
#			else:
#				logger.log("Transaction before the latest timestamp; not adding to block")

    transactionsdata = {"transactions": textarray, "signatures": signarray}
    if len(textarray) > 0:
        #		transactions={"transactions":textarray}
        logger.log("Found some transactions; adidng to chain")
    else:
        logger.log("No new transactions,checking for time.")
        logger.log("latest ts:", latest_ts, "\tNow: ", datetime.datetime.now())
        logger.log("Time since last block: ", round(
            (datetime.datetime.now() - latest_ts).total_seconds(), 2), " seconds")
        # no transactions for 1 hours
        if (datetime.datetime.now() - latest_ts).total_seconds() < 30:  # TODO - Change the block time limit
            logger.log(
                "No new transactions, not enough time since last block. Exiting.")
            # exit();
            return logger.get_logs()
            return False
        else:
            logger.log("More than ", block_time_limit,
                       " hours since the last block, adding a new empty one")

#    con = sqlite3.connect(NEWRL_DB)
#    cur = con.cursor()
    print(transactionsdata)
    block = blockchain.mine_block(cur, transactionsdata)
    # the chain is updated. Now we update the state db using transaction data
    update_db_states(cur, block['index'], transactionsdata['transactions'])
    con.commit()
    con.close()

    broadcast_block(block)
    return logger.get_logs()

def broadcast_block(block):
    peers = get_peers()

    private_key = _private
    public_key = _public
    signature = {
        'public_key': public_key,
        'msgsign': sign_object(private_key, block)
    } 
    block_payload = {
        'block_index': block['index'],
        'hash': calculate_hash(block),
        'data': block,
        'signature': signature
    }

    print(json.dumps(block_payload))

    for peer in peers:
        url = 'http://' + peer['address'] + ':' + str(NEWRL_PORT)
        print('Broadcasting to peer', url)
        try:
            requests.post(url + '/receive-block', json={'block': block_payload}, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f'Error broadcasting block to peer: {url}')
            print(e)
    return True    
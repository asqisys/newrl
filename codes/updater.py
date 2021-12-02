# Python programm to create object that enables addition of a block

import datetime
import json
import os
import shutil

from .constants import STATE_FILE, CHAIN_FILE, MEMPOOL_PATH
from codes.utils import BufferedLog
from codes.blockchain import Blockchain
from codes.transactionmanager import Transactionmanager
from codes.chainscanner import Chainscanner, get_wallet_token_balance

import sqlite3


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
    globaldir = "/data/asqi/newrl/"
    #blockchain = Blockchain("inginesis.json")
    blockchain = Blockchain()
    cs_prev = Chainscanner(CHAIN_FILE)
#	blockchain = Blockchain();
#	blockchain.loadfromfile("chain.json");



    destchain = globaldir+CHAIN_FILE
    deststate = globaldir+STATE_FILE
    if os.path.exists(destchain):
        logger.log("Found global chain. Checking for match with local.")
        globalchain = Blockchain(destchain)
        if globalchain.chain_valid(globalchain.chain):
            if chainmatch(globalchain.chain, blockchain.chain):
                logger.log(
                    "Global chain matching local chain available, checking for update.")
                if len(globalchain.chain) <= len(blockchain.chain):
                    logger.log(
                        "Chains are of matching and local chain is longer or of same length, not updating local.")
                else:
                    logger.log(
                        "Chains are of matching but global longer than local, updating local file and loading it again.")
                    shutil.copy(destchain, CHAIN_FILE)
                    blockchain = Blockchain(CHAIN_FILE)
            else:
                logger.log(
                    "Global chain does not match local chain. Investigae. Not copying to local but continuing with local-only update.")
        else:
            logger.log(
                "Global chain is not valid, investigate. Continuing with local-only update.")
    else:
        logger.log("No global chain found. Continuing with local-only update.")

    max_block_height = 10
    block_time_limit = 1  # number of hours of no transactions still prompting new block
    block_height = 0
    latest_ts = blockchain.get_latest_ts()

    mempool = MEMPOOL_PATH
    # incltrans = options.itpool
    filenames = os.listdir(mempool)  # this is the mempool
    logger.log("Files in mempool: ", filenames)
    textarray = []
    signarray = []
    transfiles = []
    validationfiles = []
    tmtemp = Transactionmanager()
    for filename in filenames:
        if "validation" in filename:  # the validation files
            validationfiles.append(filename)
        if "transaction" in filename:
            transfiles.append(filename)

    con = sqlite3.connect('../newrl.db')
    cur = con.cursor()
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
#			logger.log(transaction)
            ts = datetime.datetime.strptime(
                transaction["timestamp"][:-7], "%Y-%m-%d %H:%M:%S")
#			logger.log(ts)
#			if ts > latest_ts:
#				logger.log("Found transaction after latest_ts with ts = ",ts)
    #			logger.log(transaction['valid'])

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
        #	if transaction['valid']==1:
            traninclusionflag = False
            if tranvalidity == 1:
                #	logger.log("Found valid transaction, adding to block. Moving file to ",incltrans)
                logger.log(
                    "Found valid transaction, checking if it is already included")
                # alltranids = cs_prev.getalltransids()
                transactions_cursor = cur.execute('SELECT * FROM transactions where transaction_code=?', (transaction['trans_code'])).fetchall()
                row = transactions_cursor.fetchone()
                if row is not None:
                    traninclusionflag = True
                    continue
                # for tranid in alltranids:
                #     if tranid['trans_code'] == transaction['trans_code']:
                #         logger.log(
                #             "Transaction with id ", transaction['trans_code'], " is already included in block number ", tranid['blockindex'])
                #         traninclusionflag = True
                #         break
                if traninclusionflag:  # the current transaction is already included in some earlier block
                    continue  # this takes the process to the next transaction

                textarray.append(transaction)
                signarray.append(signatures)
                # try:
                # 	shutil.move(file, incltrans);
                # except:
                # 	logger.log("Couldn't move,",file);
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
            (datetime.datetime.now() - latest_ts).total_seconds()/3600, 2), " hours")
        # no transactions for 1 hours
        if (datetime.datetime.now() - latest_ts).total_seconds() < 3600*block_time_limit:
            logger.log(
                "No new transactions, not enough time since last block. Exiting.")
            # exit();
            return logger.get_logs()
            return False
        else:
            logger.log("More than ", block_time_limit,
                       " hours since the last block, adding a new empty one")

    blockchain.mine_block(transactionsdata)
    # the chain is updated. Now we update the state db using transaction data
    update_db_states(transactionsdata['transactions'])

#     if blockchain.chain_valid(blockchain.chain):
#         #		chainjsonstr=json.dumps(blockchain.chain);
#         with open(CHAIN_FILE, "w") as chainwrite:
#             json.dump(blockchain.chain, chainwrite)
#         logger.log("Wrote to ", CHAIN_FILE)
#         # updating state now
#         cs = Chainscanner(CHAIN_FILE)
#         all_wallets = cs.getallwallets()
#         all_tokens = cs.getalltokens()
#         all_balances = cs.getallbalances()
#         newstate = {'all_wallets': all_wallets,
#                     'all_tokens': all_tokens, 'all_balances': all_balances}
# #		update_db_states(newstate)
#         # if os.path.exists(STATE_FILE):
#         # 	ts=str(datetime.datetime.now());
#         # 	statearchivefile='./statearchive/statefile_'+ts[0:10]+"-"+ts[-6:]+".json"
#         # 	shutil.move(STATE_FILE,statearchivefile)
#         # 	logger.log("Moved existing state file - ",STATE_FILE," - to ",statearchivefile)
#         with open(STATE_FILE, 'w') as writefile:
#             json.dump(newstate, writefile)
#             logger.log("Wrote new state to ", STATE_FILE)

#         logger.log("Local chain updated. Now attempting to update global chain.")
#         destchain = globaldir+CHAIN_FILE
#         deststate = globaldir+STATE_FILE
#         if os.path.exists(destchain):
#             logger.log("Found global chain to update")
#             try:
#                 with open(destchain, "r") as gcfile:
#                     globalchain = json.load(gcfile)
#                 logger.log("Loaded globalchain")
#             except:
#                 logger.log(
#                     "Could not load globalchain. Exiting without updating global. Investigate.")
#                 globalchain = []
#                 return logger.get_logs()
#                 # return True

#             # globalchain exists but does not match, exit
#             if not chainmatch(globalchain, blockchain.chain):
#                 logger.log(
#                     "Common portion of global and local chains do not match. Not updating global chain.")
#                 return logger.get_logs()
#                 # return True	#important to exit to avoid copying local to global
#         try:
#             # if globalchain does not exist, this will create it
#             shutil.copy(CHAIN_FILE, destchain)
#             logger.log("Updated global chain with local copy.")
#             os.chmod(destchain, 0o666)
#             logger.log("Changed mode to 666")
#         except:
#             logger.log(
#                 "Couldn't upload global chain or change its mode to 666, investigate.")
#         try:
#             shutil.copy(STATE_FILE, deststate)
#             logger.log("Updated global state with local copy.")
#             os.chmod(deststate, 0o666)
#             logger.log("Changed mode to 666")
#         except:
#             logger.log(
#                 "Couldn't update global state or change its mode to 666, investigate.")

#     else:
#         logger.log("Invalid blockchain, not changing anything.")

    return logger.get_logs()
#	logger.log(blockchain.chain)
#	logger.log(blockchain.get_latest_ts())


def update_db_states(transactions):
    con = sqlite3.connect('../newrl.db')
    cur = con.cursor()

    for transaction in transactions:
        transaction_data = transaction['specific_data']

        if transaction['type'] == 1:  # this is a wallet creation transaction
            wallet = transaction_data
            kyc_doc_json = get_kyc_doc_hash_json(
                wallet['kyc_docs'], wallet['kyc_doc_hashes'])
            data_json = json.dumps(wallet['specific_data'])
            query_params = (wallet['wallet_address'],
                            wallet['wallet_public'],
                            wallet['custodian_wallet'],
                            kyc_doc_json,
                            wallet['ownertype'],
                            wallet['jurisd'],
                            data_json
                            )
            cur.execute(f'''INSERT OR IGNORE INTO wallets
					(wallet_address, wallet_public, custodian_wallet, kyc_docs, owner_type, jurisdiction, specific_data)
					VALUES (?, ?, ?, ?, ?, ?, ?)''', query_params)

        if transaction['type'] == 2:  # this is a token creation transaction
            token = transaction_data
            token_attributes_json = json.dumps(token['tokenattributes'])
            query_params = (
                token['tokencode'],
                token['tokenname'],
                token['tokentype'],
                token['first_owner'],
                token['custodian'],
                token['legaldochash'],
                token['amount_created'],
                token['value_created'],
                token['sc_flag'],
                token_attributes_json
            )
            cur.execute(f'''INSERT OR IGNORE INTO tokens
				(tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, amount_created, value_created, sc_flag, token_attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)

            balance = get_wallet_token_balance(
                cur, token['first_owner'], token['tokencode'])
            balance = balance + token['amount_created']
            update_wallet_token_balance(
                cur, token['first_owner'], token['tokencode'], balance)

        if transaction['type'] == 4 or transaction['type'] == 5:  # this is a transfer tx
            sender1 = transaction_data['wallet1']
            sender2 = transaction_data['wallet2']

            tokencode1 = transaction_data['asset1_code']
            amount1 = int(transaction_data['asset1_number'] or 0)
            transfer_tokens_and_update_balances(
                cur, sender1, sender2, tokencode1, amount1)

            tokencode2 = transaction_data['asset2_code']
            amount2 = int(transaction_data['asset2_number'] or 0)
            transfer_tokens_and_update_balances(
                cur, sender2, sender1, tokencode2, amount2)

    con.commit()
    con.close()


def transfer_tokens_and_update_balances(cur, sender, reciever, tokencode, amount):
    sender_balance = get_wallet_token_balance(cur, sender, tokencode)
    reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
    sender_balance = sender_balance - amount
    reciever_balance = reciever_balance + amount
    update_wallet_token_balance(cur, sender, tokencode, sender_balance)
    update_wallet_token_balance(cur, reciever, tokencode, reciever_balance)


def update_wallet_token_balance(cur, wallet_address, token_code, balance):
    cur.execute(f'''INSERT OR REPLACE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet_address, token_code, balance))


def get_kyc_doc_hash_json(kyc_docs, kyc_doc_hashes):
    doc_list = []
    for idx, doc in enumerate(kyc_docs):
        doc_list.append({
            'type': doc,
            'hash': kyc_doc_hashes[idx]
        })
    return json.dumps(doc_list)

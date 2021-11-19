# Python programm to create object that enables addition of a block

import datetime
import hashlib
import json

import sqlite3


class Blockchain:

    def __init__(self, genesisfile=None):
        self.con = sqlite3.connect('newrl.db')
        self.cur = self.con.cursor()

        self.chain = []
        self.genesisfile = genesisfile
        if genesisfile:
            self.loadfromfile(genesisfile)
#			with open(genesisfile,"r") as file:
#				print("Starting with genesis file: ",genesisfile)
#				chain=json.load(file);
#				block = chain[0];
            block = self.chain[0]
        else:
            print("No genesis file, starting new chain with standard genesis params.")
            timestamp = str(datetime.datetime.now())
            transactions = [{'timestamp': timestamp, 'type': 0, 'currency': "INR", 'fee': 0.0,
                             'descr': "Genesis Block", 'valid': 1, 'block_index': 0, 'specific_data': []}]
            block = {'index': 1,
                     'timestamp': timestamp,
                     'proof': 0,
                     'text': {'transactions': transactions},
                     'previous_hash': 0}
            proof = self.proof_of_work(block)
            self.create_block(block['timestamp'], proof, 0, block['text'])
            if self.chain_valid(self.chain):
                with open("inginesis.json", "w") as chainwrite:  # "inginesis.json"
                    json.dump(self.chain, chainwrite)
                print("Overwrote inginesis.json")  # "inginesis.json"

#		print("Genesis block is \n",block,"\n")
#		print("The hash of genesis block is ",self.hash(block),"\n")
#		self.create_block(block['timestamp'],block['proof'], 0, block['text'])

    def create_block(self, timestamp, proof, previous_hash, text):
        print("adding a block")
        block_index = self.get_last_block_index() + 1
        block = {'index': block_index,
                 'timestamp': timestamp,
                 'proof': proof,
                 'text': text,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        block_hash = self.hash(block)
        transactions_hash = self.hash(text['transactions'])
        db_block_data = (block_index, timestamp, proof,
                         previous_hash, block_hash, transactions_hash)
        self.cur.execute('INSERT OR IGNORE INTO blocks (block_index, timestamp, proof, previous_hash, hash, transactions_hash) VALUES (?, ?, ?, ?, ?, ?)', db_block_data)
        self.con.commit()
        return block

    def get_last_block_index(self):
        last_block_cursor = self.cur.execute(
            f'''SELECT block_index FROM blocks ORDER BY block_index DESC LIMIT 1''')
        last_block = last_block_cursor.fetchone()
        return last_block[0] if last_block_cursor is not None else 0

    # proof of work which takes a block with proof set as 0 as input and returns the proof that makes its hash start with 0000
    def proof_of_work(self, block):
        new_proof = 1
        check_proof = False
        n = 0
#		print("Starting proof of work");
        while check_proof is False:
            n = n + 1
#			print("Going for the ",n,"th time");
            block['proof'] = new_proof
            encoded_block = json.dumps(block, sort_keys=True).encode()
            hash_operation = hashlib.sha256(encoded_block).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
#		print("Starting validity check")
#		print("chain len: ",len(chain))
        while block_index < len(chain):
            block = chain[block_index]
#			print(block['previous_hash'])
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            text = block['text']
            encoded_block = json.dumps(block, sort_keys=True).encode()
            hash_operation = hashlib.sha256(encoded_block).hexdigest()

            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
#		print("Out of the loop")
        return True

# Mining a new block
    def mine_block(self, text):
        print("starting the mining step 1")
        last_block_cursor = self.cur.execute(
            'SELECT hash FROM blocks ORDER BY block_index DESC LIMIT 1')
        last_block = last_block_cursor.fetchone()
        previous_hash = last_block[0] if last_block is not None else 0
        # print(last_block)
        # previous_block = self.chain[-1]
#		print(previous_block);
        # previous_hash = self.hash(previous_block)
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': 0,
                 'text': text,
                 'previous_hash': previous_hash}

        proof = self.proof_of_work(block)
        print("Current block proof: ", proof)
#		print("previous_hash = ",previous_hash)
        block = self.create_block(
            block['timestamp'], proof, previous_hash, text)

        response = {'message': 'A block is MINED',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previous_hash': block['previous_hash']}
        block_index = block['index']
        self.add_transactions_to_block(block_index, text['transactions'])
        return response

    def get_latest_ts(self):
        chain = self.chain
        if len(chain) < 1:
            print("very short chain; returning with min ts as latest")
            latest_ts = datetime.datetime.strptime(
                "2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
            return latest_ts
        latest_block = chain[len(chain)-1]
#		if len(chain)==1:
#			return latest_block['timestamp'][:-7]
        try:
            transactions = latest_block['text']['transactions']
#			print("transactions of latest block are ",transactions)
#			latest_ts = datetime.datetime.strptime("2000-01-01 00:00:00" ,"%Y-%m-%d %H:%M:%S");
            latest_ts = datetime.datetime.strptime(
                latest_block['timestamp'][:-7], "%Y-%m-%d %H:%M:%S")
            # the above is useful for empty blocks
            for transaction in transactions:
                ts = datetime.datetime.strptime(
                    transaction['timestamp'][:-7], "%Y-%m-%d %H:%M:%S")
#				print("ts of a ne trans : ",ts)
                if ts > latest_ts:
                    latest_ts = ts
        except:
            latest_ts = datetime.datetime.strptime(
                latest_block['timestamp'][:-7], "%Y-%m-%d %H:%M:%S")
        return latest_ts

    def add_transactions_to_block(self, block_index, transactions):
        print(block_index, transactions)
        for transaction in transactions:
            specific_data = json.dumps(
                transaction['specific_data']) if 'specific_data' in transaction else ''
            db_transaction_data = (
                block_index,
                transaction['trans_code'],
                transaction['timestamp'],
                transaction['type'],
                transaction['currency'],
                transaction['fee'],
                transaction['descr'],
                transaction['valid'],
                specific_data
            )
            self.cur.execute(f'''INSERT OR IGNORE INTO transactions
				(block_index, transaction_code, timestamp, type, currency, fee, description, valid, specific_data)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', db_transaction_data)

    def loadfromfile(self, chainfile):
        try:
            with open(chainfile, "r") as read_file:
                chainfromfile = json.load(read_file)
        except:
            print("No chain file found. Exiting.")
            exit()
        # latest_ts = self.get_latest_ts(chainfromfile);	#not valid as of now since arg is not a blockchain object
        genesis_ts = chainfromfile[0]['timestamp']
#		genfile=self.genesisfile

        # tempchain=Blockchain(genfile);
        # print(tempchain.chain_valid(tempchain.chain));

# def load_chain(chainlist):
#        chainaslist = chainlist;
#		chainaslist = chainfromfile
#	        ts = chainaslist[0]['timestamp']
#        newchain = Blockchain(ts);
#	        newchain = Blockchain(chainfile)	#chainfile also includes a genesis block so that's what we use to init

        # we need to confirm that genesis block is valid in the loaded chain
        self.chain = chainfromfile
        if self.chain_valid(self.chain):
            print("Loaded chain from ", chainfile, ", and it is valid.")
            return True
        else:
            print("Tried to load chain from ", chainfile,
                  ", but the chain is invalid.")
            return False
#			exit;

    # the below code is not needed since we are already insde the bc object here
#	        previous_block = chainaslist[0];
#	        block_index = 1;
#	        while block_index < len(chainaslist):
#        	        block=chainaslist[block_index];
#	                proof = block['proof']
#        	        text = block['text']
#	                timestamp = block['timestamp']
#        	        previous_hash= block['previous_hash'];
#                	newblock = newchain.create_block(timestamp, proof, previous_hash, text)
#	                block_index += 1;
#        	return newchain;

# Python programm to create object that enables addition of a block

import json
import sqlite3

from codes.blockchain import Blockchain

class Chainscanner():

    def __init__(self, chainfile="chain.json"):
        self.blockchain = Blockchain(chainfile)
#        print("Loaded chain from ",chainfile)
        self.chainlength=len(self.blockchain.chain)
        self.latestts=self.blockchain.get_latest_ts()
        self.con = sqlite3.connect('newrl.db')
        self.cur = self.con.cursor()

    def chainstatus(self):
        if self.blockchain.chain_valid(self.blockchain.chain):
#            print("Chain loaded is valid")
            return True
        else:
            return False
#            print("Invalid blockchain.")

#    def chainlength(self):
#        return len(blockchain.chain)

    def gettransactions(self,blockindex):
    #    print("Blockindex looking for ", blockindex)
        transactions=self.blockchain.chain[blockindex-1]['text']['transactions']
        return transactions

    def getbalancesbytoken(self,tokencode):
        #function to scan through the chain and produce an array of wallet addresses, and their balances by token codes
        balances = []
        wallets = self.getallwallets()
#        tokens = self.getalltokens()
#        for index in (1,self.chainlength+1):    #blockindex starts at 1 and not 0
#            transactions=self.gettransactions(index)
        for wallet in wallets:
            balance = self.getbaladdtoken(wallet['wallet_address'],tokencode)
            balances.append({'wallet_address':wallet['wallet_address'],'balance':balance})
        return balances
        
    def getalltransids(self):
        tranids=[]
        index=1
        while index<self.chainlength+1:
            transactions=self.gettransactions(index)
            blindex=index    
            print("searching in block no ",blindex)
            index+=1
            if len(transactions)<1:
                continue
            for transaction in transactions:
                try:
                    tranids.append({"trans_code":transaction['trans_code'],"blockindex":blindex})
                except:
                    continue
        return tranids

    def getallwallets(self):
        wallets=[]
        index=1
    #    with open("creatorwalletdata.json","r") as readfile:
    #        cwall=json.load(readfile)
    #    cadd=cwall['address']
    #    creatorwallet={'wallet_address':cadd,
    #            'custodian_wallet':cadd,
    #            'kyc_docs':[],
    #            'kyc_doc_hashes':[],
    #            'ownertype':1,
    #            'jurisd':2,
    #            'specific_data':[]
    #            }
    #    wallets.append(creatorwallet)
        while index<self.chainlength+1:
#        for index in (1,self.chainlength+1):    #blockindex starts at 1 and not 0
            transactions=self.gettransactions(index)
            index+=1
            if len(transactions)<1:
                continue
            for transaction in transactions:
                if transaction['type']==0:    #this is the genesis transaction
                    walletdata={'wallet_address':transaction['specific_data']['creator'],
                        'wallet_public':transaction['specific_data']['creatorpublic'],
                        'custodian_wallet':transaction['specific_data']['creator'],
                        'kyc_docs':[],
                        'kyc_doc_hashes':[],
                        'ownertype':1,
                        'jurisd':2,
                        'specific_data':[{"remarks":"creator's wallet"}]}
                    wallets.append(walletdata)

                if transaction['type']==1:    #this is a wallet creation transaction
            #        print(transaction)
                    walletdata={'wallet_address':transaction['specific_data']['wallet_address'],
                        'wallet_public':transaction['specific_data']['wallet_public'],
                        'custodian_wallet':transaction['specific_data']['custodian_wallet'],
                        'kyc_docs':transaction['specific_data']['kyc_docs'],
                        'kyc_doc_hashes':transaction['specific_data']['kyc_doc_hashes'],
                        'ownertype':transaction['specific_data']['ownertype'],
                        'jurisd':transaction['specific_data']['jurisd'],
                        'specific_data':transaction['specific_data']['specific_data']}        
#                    wallets.append(transaction['specific_data']['wallet_public'])
                    wallets.append(walletdata)
        return wallets

    def getalltokens(self):
        tokens=[]
        idx=1
#        for idx in (1,self.chainlength+1):    #blockindex starts at 1 and not 0
        while idx<self.chainlength+1:
            transactions=self.gettransactions(idx)
        #    print("searching tokens in ",idx)
            idx+=1
            if len(transactions)<1:
            #    print("no transactions in this block")
                continue
        #    print("found some trans")
            for transaction in transactions:
                if transaction['type']==2:      #this is a token creation transaction
            #        print("found token creation")
                #    tokendata=0
                    tokens.append(transaction['specific_data'])            
        return tokens

    def getallbalances(self):
        balances = []
        tokens=self.getalltokens()
        wallets = self.getallwallets()
        for wallet in wallets:
#            tokenbal={}
            for token in tokens:
                balance=self.getbaladdtoken(wallet['wallet_address'],token['tokencode'])
#                tokenbal.update({token,balance})
                balances.append({'wallet_address':wallet['wallet_address'],'tokencode':token['tokencode'],'balance':balance})
                print({'wallet_address':wallet['wallet_address'],'tokencode':token['tokencode'],'balance':balance})
        return balances
    
    def createbalancesfile(self,file='all_balances.json'):
        allbal=self.getallbalances()
        with open(file,'w') as writefile:
            json.dump(allbal,writefile)
        print("Dumped all balances data to ",file)

    def getbalancesbyaddress(self, address):
        #function to get balances of all tokens for a given address
        balances = []
        tokens=self.getalltokens()
        for token in tokens:
            balance = self.getbaladdtoken(address,token['tokencode'])
#            balances.append('wallet_public'=address,'tokencode'=token,'balance'=balance)
            balances.append({'tokencode':token['tokencode'],'balance':balance})
        return balances
        
    def getbaladdtoken(self, address, tokencode):
        balance = self.cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {'address': address, 'tokencode': tokencode})
        for row in balance:
            return row[0]
        #function to get latest balance of a given wallet for a given token
        balance=0
        index=1
#        for index in (1,self.chainlength+1):    #blockindex starts at 1 and not 0
        #    print("index is ", index)
        while index<=self.chainlength:
            transactions=self.gettransactions(index)
#            print("block no: ",index)
#            print(transactions)
            index+=1
            if len(transactions)<1:
                continue
            for transaction in transactions:
            #    print("Transaction type is ",transaction['type'])
                if transaction['type']==2:
            #        print("checking creation transactions now")
                    if transaction['specific_data']['first_owner']==address:
                        if transaction['specific_data']['tokencode']==tokencode:
            #                print("found a balance ",transaction['specific_data']['amount_created'])
                            balance=balance+transaction['specific_data']['amount_created']
                if transaction['type']==4 or transaction['type']==5:      #this is a asset transfer transaction
                    if transaction['specific_data']['wallet1']==address:
                        if transaction['specific_data']['asset1_code']==tokencode:    #wallet1 is sending
                            balance=balance-transaction['specific_data']['asset1_number']
                        if transaction['specific_data']['asset2_code']==tokencode:      #wallet1 is recvng
                            balance=balance+transaction['specific_data']['asset2_number']
                    if transaction['specific_data']['wallet2']==address:
                        if transaction['specific_data']['asset2_code']==tokencode:      #wallet2 is sending
                            balance=balance-transaction['specific_data']['asset2_number']
                        if transaction['specific_data']['asset1_code']==tokencode:      #wallet2 is recvng
                            balance=balance+transaction['specific_data']['asset1_number']
        #        if transaction['type']==5:
                    
        return balance

    def isaddressvalid(self, address):
        #function to check if a given address is valid
        wallets=self.getallwallets()
        for wallet in wallets:
            if wallet['wallet_address']==address:
                return True
        return False

def get_wallet_token_balance(cur, wallet_address, token_code):
    balance_cursor = cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
                    'address': wallet_address, 'tokencode': token_code})
    balance_row = balance_cursor.fetchone()
    balance = balance_row[0] if balance_row is not None else 0
    return balance


def download_state():
    con = sqlite3.connect('newrl.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    wallets_cursor = cur.execute('SELECT * FROM wallets').fetchall()
    wallets = [dict(ix) for ix in wallets_cursor]

    tokens_cursor = cur.execute('SELECT * FROM tokens').fetchall()
    tokens = [dict(ix) for ix in tokens_cursor]

    balances_cursor = cur.execute('SELECT * FROM balances').fetchall()
    balances = [dict(ix) for ix in balances_cursor]

    state = {
        'wallets': wallets,
        'tokens': tokens,
        'balances': balances,
    }
    return state

def download_chain():
    con = sqlite3.connect('newrl.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    blocks_cursor = cur.execute('SELECT * FROM blocks').fetchall()
    blocks = [dict(ix) for ix in blocks_cursor]
    for idx, block in enumerate(blocks):
        print(block)
        transactions_cursor = cur.execute('SELECT * FROM transactions where block_index=' + str(block['block_index'])).fetchall()
        transactions = [dict(ix) for ix in transactions_cursor]
        block[idx] = {
            'text': {
                'transactions': transactions
            }
        }
    print(blocks)
    
    chain = blocks
    return chain
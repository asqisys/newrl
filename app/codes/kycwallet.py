# program to create and manage objects for wallets
import codecs
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import json
import datetime
import base64

from ..constants import TMP_PATH
from .transactionmanager import Transactionmanager


def get_address_from_public_key(public_key):
    public_key_bytes = base64.b64decode(public_key)

    hash = keccak.new(digest_bits=256)
    hash.update(public_key_bytes)
    keccak_digest = hash.hexdigest()

    address = '0x' + keccak_digest[-40:]
    return address


def generate_wallet_address():
    private_key_bytes = os.urandom(32)
    keydata = {'public': None, 'private': None, 'address': None}
    key = ecdsa.SigningKey.from_string(
        private_key_bytes, curve=ecdsa.SECP256k1).verifying_key

    key_bytes = key.to_string()
    public_key = codecs.encode(key_bytes, 'hex')

    # the below section is to enable serialization while passing the keys through json
    private_key_final = base64.b64encode(private_key_bytes).decode('utf-8')
    public_key_final = base64.b64encode(key_bytes).decode('utf-8')
    keydata['address'] = get_address_from_public_key(public_key_final)
    keydata['private'] = private_key_final
    keydata['public'] = public_key_final

    return keydata

def add_wallet(kyccustodian, kycdocs, ownertype, jurisd, public_key, wallet_specific_data={}):
        address = get_address_from_public_key(public_key)
        hs = hashlib.blake2b(digest_size=40)
        hs.update(address)
        personid = 'pi' + hs.hexdigest()

        wallet = {
            'personid':personid,
            'custodian_wallet': kyccustodian,
            'kyc_docs': kycdocs,
            'ownertype': ownertype,
            'jurisd': jurisd,
            'specific_data': wallet_specific_data,
            'wallet_address': address,
            'wallet_public': public_key,
        }
        
        trans = transactioncreator(wallet)
        ts = str(datetime.datetime.now())
        file = TMP_PATH + "transaction-1-" + ts[0:10] + "-" + ts[-6:] + ".json"
        transactionfile = trans.dumptransaction(file)
        return transactionfile

def add_linked_wallet(currentaddress, public_key, wallet_specific_data={}):
        address = get_address_from_public_key(public_key)
        #code to get personid and other details from currentaddress 
        personid = None
        kycdocs = None
        ownertype = None
        jurisd = None
        #signed by currentaddress owner, not kyccustodian, do not get that data
        wallet = {
            'personid':personid,
            'custodian_wallet': currentaddress,
            'kyc_docs': kycdocs,
            'ownertype': ownertype,
            'jurisd': jurisd,
            'specific_data': wallet_specific_data,
            'wallet_address': address,
            'wallet_public': public_key,
        }
        
        trans = transactioncreator(wallet)
        ts = str(datetime.datetime.now())
        file = TMP_PATH + "transaction-1-" + ts[0:10] + "-" + ts[-6:] + ".json"
        transactionfile = trans.dumptransaction(file)
        return transactionfile

def generate_wallet(kyccustodian, kycdocs, ownertype, jurisd, wallet_specific_data={}):
        newkeydata = generate_wallet_address()
        hs = hashlib.blake2b(digest_size=40)
        hs.update(address)
        personid = 'pi' + hs.hexdigest()        
        wallet = {
            'personid': personid,
            'custodian_wallet': kyccustodian,
            'kyc_docs': kycdocs,
            'ownertype': ownertype,
            'jurisd': jurisd,
            'specific_data': wallet_specific_data,
            'wallet_address': newkeydata['address'],
            'wallet_public': newkeydata['public'],
        }
        
        print("Now adding transaction")
        trans = transactioncreator(wallet)
        ts = str(datetime.datetime.now())
        file = TMP_PATH + "transaction-1-" + ts[0:10] + "-" + ts[-6:] + ".json"
        transactionfile = trans.dumptransaction(file)
        return transactionfile

def transactioncreator(wallet):
        transaction_data = {
            'timestamp': str(datetime.datetime.now()),
            'type': 1,
            'currency': 'INR',
            'fee': 0.0,
            'descr': 'New wallet',
            'valid': -1,
            'specific_data': wallet
        }
        transaction_data = {'transaction': transaction_data, 'signatures': []}
        transaction_manager = Transactionmanager()
        transaction_manager.transactioncreator(transaction_data)
        return transaction_manager

def get_digest(file_path):
        h = hashlib.sha256()

        with open(file_path, 'rb') as file:
            while True:
                # Reading is buffered, so we can read smaller chunks.
                chunk = file.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

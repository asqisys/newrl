# program to create and manage objects for wallets
import codecs
import ecdsa
from Crypto.Hash import keccak
import os
import hashlib
import json
import datetime
import base64

from .constants import MEMPOOL_PATH
from .transactionmanager import Transactionmanager


def get_address_from_public_key(public_key):
    public_key_bytes = codecs.decode(public_key, 'hex')

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

    keydata['address'] = get_address_from_public_key(public_key)

    # the below section is to enable serialization while passing the keys through json
    private_key_final = base64.b64encode(private_key_bytes).decode('utf-8')
    public_key_final = base64.b64encode(key_bytes).decode('utf-8')
    keydata['private'] = private_key_final
    keydata['public'] = public_key_final

    return keydata

def add_wallet(kyccustodian, kycdocs, ownertype, jurisd, public_key, wallet_specific_data={}):
        address = get_address_from_public_key(public_key)
        wallet = {
            'custodian_wallet': kyccustodian,
            'kyc_docs': kycdocs,
            'ownertype': ownertype,
            'jurisd': jurisd,
            'specific_data': wallet_specific_data,
            'wallet_address': address,
            'wallet_public': public_key,
        }
        
        trans = transactioncreator(wallet)
        transactionfile = trans.dumptransaction()
        return transactionfile


def make_wallet(kyccustodian, kycdocs, ownertype, jurisd, wallet_specific_data={}):
        newkeydata = generate_wallet_address()
        wallet = {
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
        transactionfile = trans.dumptransaction()
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

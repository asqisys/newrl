import os
import codecs
import ecdsa
from Crypto.Hash import keccak


def create_contract_address():
    private_key_bytes = os.urandom(32)
    key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
    key_bytes = key.to_string()
    public_key = codecs.encode(key_bytes, 'hex')
    public_key_bytes = codecs.decode(public_key, 'hex')
    hash = keccak.new(digest_bits=256)
    hash.update(public_key_bytes)
    keccak_digest = hash.hexdigest()
    address = 'ct' + keccak_digest[-40:]   # this overwrites the None value in the init call, whenever on-chain contract is setup
    return address
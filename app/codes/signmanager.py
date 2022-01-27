# program to create and manage objects for wallets

import json
import base64
import sqlite3

from starlette.responses import FileResponse
from .transactionmanager import Transactionmanager, get_sc_validadds
import base64
from optparse import OptionParser
from ..constants import NEWRL_DB

# this below one is useful for signing-time check


def addresschecker(transaction, address):
    #	trans=trandata['transaction']
    #	signatures = trandata['signatures']
    validadds = getvalidadds(transaction)
    print(validadds)
    for add in validadds:
        if add == address:
            print("The address ", address,
                  " is authorised to sign this transaction.")
            return True
        # did not find the address in the validadds
    print("The address ", address, " is not authorised to sign this transaction.")
    return False

# use the below one to get all authorized addresses that can sign a transaction


def getvalidadds(transaction):
    trans = transaction
    ttype = trans['type']
    validadds = []
    if ttype == 1:  # wallet creation, custodian needs to sign
        validadds.append(trans['specific_data']['custodian_wallet'])
    if ttype == 2:  # token creation, custodian needs to sign
        validadds.append(trans['specific_data']['custodian'])
    if ttype == 3:
        validadds = get_sc_validadds(trans)
    if ttype == 4:  # two way transfer; both senders need to sign
        validadds.append(trans['specific_data']['wallet1'])
        validadds.append(trans['specific_data']['wallet2'])
    if ttype == 5:  # one way transfer; only sender1 is needed to sign
        validadds.append(trans['specific_data']['wallet1'])
    if ttype == 6:  # trust score change
        validadds.append(trans['specific_data']['address1'])
    return validadds

# use the below for validator


def checkaddress(transaction, signatures):
    validadds = getvalidadds(transaction)
#	signatures = trandata['signatures']
    validsigns = 1
    sumonevalids = 0
    for signature in signatures:
        onesignvalid = 0
        for address in validadds:
            # the signatures includes a valid address
            if signature['wallet_address'] == address:
                print("The address ", signature['wallet_address'],
                      " in signature is authorised to sign this transaction.")
                onesignvalid = 1
        if not onesignvalid:
            print("The address ", signature['wallet_address'],
                  " in signature is not authorised to sign this transaction.")
        validsigns = validsigns*onesignvalid
        sumonevalids += onesignvalid
    if validsigns and sumonevalids:  # adding sum to guard against the case where there are no signatures at all
        return True
    else:
        return False


def sign(walletfile, transfile=None):
    #	wallet=Walletmanager(option.walletfile);
    #	wallet.iswalletlisted()
    pvtkeybytes = None
    pubkeybytes = None
    with open(walletfile, 'r') as file:
        data = json.load(file)
    for walletdata in data:
        # if walletdata['address']==address:
        address = walletdata['address']
        pvtkeybytes = base64.b64decode(walletdata['private'])
        pubkeybytes = base64.b64decode(walletdata['public'])
    if not pvtkeybytes:
        print("No private key found for the address")
        return False

    tm = Transactionmanager()
    tm.set_transaction_data(transfile)
#	print("Current signatures are ",tm.signatures)
    if not addresschecker(tm.transaction, address):
        return False

    signtransbytes = tm.signtransaction(pvtkeybytes, address)
    print("signed msg signature is:", signtransbytes,
          " and address is ", address)
    signtrans = base64.b64encode(signtransbytes).decode('utf-8')
#	print("storing this in encoded form is:",signtrans)
    if signtrans:
        tm.dumptransaction(transfile)
        print("Successfully signed the transaction and updated its signatures data.")
    #	print("Signatures are")
        sign_status = tm.verifysign(signtrans, pubkeybytes, address)
        print("Status of signing: ", sign_status)
        return FileResponse(transfile, filename="signed_transferfile.json")
        # return sign_status
    else:
        print("Signing failed. No change made to transaction's signature data")
        return None

# Refactored from above. above can be deleted
def sign_transaction(wallet_data, transaction_data):
    pvtkeybytes = None
    pubkeybytes = None
    
    address = wallet_data['address']
    pvtkeybytes = base64.b64decode(wallet_data['private'])
    pubkeybytes = base64.b64decode(wallet_data['public'])
    if not pvtkeybytes:
        print("No private key found for the address")
        return False

    tm = Transactionmanager()
    tm.set_transaction_data(transaction_data)
    if not addresschecker(tm.transaction, address):
        return False

    signtransbytes = tm.signtransaction(pvtkeybytes, address)
    print("signed msg signature is:", signtransbytes,
          " and address is ", address)
    signtrans = base64.b64encode(signtransbytes).decode('utf-8')
#	print("storing this in encoded form is:",signtrans)
    if signtrans:
        transaction_file = tm.dumptransaction()
        print("Successfully signed the transaction and updated its signatures data.")
        sign_status = tm.verifysign(signtrans, pubkeybytes, address)
        print("Status of signing: ", sign_status)
        with open(transaction_file) as f:
            return json.load(f)
        # return FileResponse(transfile, filename="signed_transferfile.json")
        # return sign_status
    else:
        print("Signing failed. No change made to transaction's signature data")
        return None
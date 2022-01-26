# Python programm to validate trnasctions starting with state.json and mempool

# in current version, it edits the transaction file or at least creates a new version of it post validation.. this works for permissioned variatn.. later, for decentralize dversion, we will need to alter the file altering with new validation receipt creation..

import datetime
import json
import os

from app.codes.p2p.transport import send
from .transactionmanager import Transactionmanager
from ..constants import MEMPOOL_PATH


def validate(transaction):
    #blockchain = Blockchain("inginesis.json")
    #	blockchain = Blockchain(options.chainfile)
    #	blockchain = Blockchain();
    #	blockchain.loadfromfile("chain.json");

    ts = str(datetime.datetime.now())
    tm = Transactionmanager()
    tm.set_transaction_data(transaction)
    econ = tm.econvalidator()
    signvalid = tm.verifytransigns()
    valid = 0
    if econ and signvalid:
        #		tm.dumptransaction(options.transfile);
        msg = "All well"
        valid = 1
    if not econ:
        msg = "Economic validation failed"
    if not signvalid:
        msg = "Invalid signatures"
    check = {'valid': valid, 'msg': msg}

    checkfile = MEMPOOL_PATH+tm.transaction['trans_code'] + \
        "_validation"+str("-"+ts[0:10]+"-"+ts[-6:]+".json")
    with open(checkfile, "w") as ckfile:
        json.dump(check, ckfile)

    if valid == 1:  # econ and signvalid are both True
        transoutputfile = MEMPOOL_PATH + "transaction-" + \
            str(tm.transaction['type']) + "-" + \
            tm.transaction['trans_code'] + ".json"
        tm.dumptransaction(transoutputfile)
        payload = {
            'operation': 'send_transaction',
            'data': tm.get_transaction()
        }
        # Send to transport server
        try:
            send(payload)
        except:
            print('Error sending transaction to transport server')

    status = f"Wrote check status as {check} to {checkfile}"
    print(status)
    return status

from audioop import add
from random import random
import token
from fastapi.testclient import TestClient
from ..migrations.init import init_newrl
import random
import datetime
import time

from ..main import app
from ..codes.contracts.nusd1 import nusd1

client = TestClient(app)

init_newrl()

def create_wallet():
    response = client.get("/generate-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    assert wallet['address']
    assert wallet['public']
    assert wallet['private']

    response = client.post('/add-wallet', json={
        "custodian_address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
        "ownertype": "1",
        "jurisdiction": "910",
        "kyc_docs": [
            {
                "type": 1,
                "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401"
            }
        ],
        "specific_data": {},
        "public_key": wallet['public']
    })

    print(response.text)
    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    custodian_wallet = {
        "address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==",
        "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="
    }

    response = client.post('/sign-transaction', json={
        "wallet_data": custodian_wallet,
        "transaction_data": unsigned_transaction
    })

    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    response = client.post('/run-updater', json=signed_transaction)
    assert response.status_code == 200

    response = client.get('/download-state')
    assert response.status_code == 200
    state = response.json()

    wallets = state['wallets']
    wallet_in_state = next(
        x for x in wallets if x['wallet_address'] == wallet['address'])
    assert wallet_in_state
    return wallet


def create_token(wallet, custodian_wallet, amount):
    response = client.post('/add-token', json={
        "token_name": "testSMT",
        "token_code" : "",
        "token_type": "2",
        "first_owner": wallet['address'],
        "custodian": custodian_wallet['address'],
        "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
        "amount_created": amount,
        "value_created": 1,
        "disallowed_regions": [],
        "is_smart_contract_token": False,
        "token_attributes": {}
    })

    postedval = {"token_name": "testSMT",
        "tokencode" : "",
        "token_type": "2",
        "first_owner": wallet['address'],
        "custodian": custodian_wallet['address'],
        "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
        "amount_created": amount,
        "value_created": 1,
        "disallowed_regions": [],
        "is_smart_contract_token": False,
        "token_attributes": {}}
    print(postedval)

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = client.post('/sign-transaction', json={
        "wallet_data": custodian_wallet,
        "transaction_data": unsigned_transaction
    })

    print("adding token")
    assert response.status_code == 200
    signed_transaction = response.json()
    print("signing tx")
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    print("validating tx")
    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    print("running updater")
    response = client.post('/run-updater', json=signed_transaction)
    assert response.status_code == 200

    response = client.get('/download-state')
    assert response.status_code == 200
    state = response.json()

    tokens = state['tokens']
    token_in_state = next(
        x for x in tokens if x['parent_transaction_code'] == signed_transaction['transaction']['trans_code'])
    assert token_in_state
    print("token exists in state")

    balances = state['balances']
    balance = next(x for x in balances if x['wallet_address'] ==
                   wallet['address'] and x['tokencode'] == token_in_state['tokencode'])
    assert balance
    print("token exists in balances")
    assert balance['balance'] == amount
    print("token balance correct, returning tokencode")

    return token_in_state['tokencode']


def create_transfer(wallet1, wallet2, token1, token2):
    response = client.post('/add-transfer', json={
        "transfer_type": 4,
        "asset1_code": token1,
        "asset2_code": token2,
        "wallet1_address": wallet1['address'],
        "wallet2_address": wallet2['address'],
        "asset1_qty": 1000,
        "asset2_qty": 2000
    })

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = client.post('/sign-transaction', json={
        "wallet_data": wallet1,
        "transaction_data": unsigned_transaction
    })
    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = client.post('/sign-transaction', json={
        "wallet_data": wallet2,
        "transaction_data": signed_transaction
    })
    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 2

    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    response = client.post('/run-updater')
    assert response.status_code == 200


    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token1,
        "wallet_address": wallet1['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 7888

    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token2,
        "wallet_address": wallet1['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 2000

    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token1,
        "wallet_address": wallet2['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 1000

    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": token2,
        "wallet_address": wallet2['address']
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == 6888

def add_trust_score(wallet1, wallet2, tscore):
    response = client.post('/update-trustscore', json={
        "source_address": wallet1['address'],
        "destination_address": wallet2['address'],
        "tscore": tscore
    })
    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = client.post('/sign-transaction', json={
        "wallet_data": wallet1,
        "transaction_data": unsigned_transaction
    })
    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    response = client.post('/run-updater')
    assert response.status_code == 200

def get_token_from_tx(txcode):
    response = client.get('/download-state')
    assert response.status_code == 200
    state = response.json()

    tokens = state['tokens']
    token_in_state = None
    token_in_state = next(
        x for x in tokens if x['parent_transaction_code'] == txcode)
    if token_in_state:
        return token_in_state['tokencode']
    else:
        return False

def create_contract(wallet1, signatories, contractspecs):
    response = client.get("/generate-contract-address")
    assert response.status_code == 200
    address = response.json()
    assert address
    print("created contract with address: ",address)

    response = client.post('/add-sc', json={
        "sc_address": address,
        "sc_name": "secloan1",
        "version": "1.0.0",
        "creator": wallet1['address'],
        "actmode": "hybrid",
        "signatories": signatories,
        "contractspecs": contractspecs,
        "legalparams": {}
    })

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

    response = client.post('/sign-transaction', json={
        "wallet_data": wallet1,
        "transaction_data": unsigned_transaction
    })
    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    response = client.post('/run-updater')
    assert response.status_code == 200

    return address

def call_contract(contractaddress, funct, wallet1, params):
    response = client.post('/call-sc', json={
        "sc_address": contractaddress,
        "function_called": funct,
        "signers": [wallet1['address']],
        "params": params
    })

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0
    tcode = unsigned_transaction['transaction']['trans_code']
    response = client.post('/sign-transaction', json={
        "wallet_data": wallet1,
        "transaction_data": unsigned_transaction
    })
    assert response.status_code == 200
    signed_transaction = response.json()
    assert signed_transaction['transaction']
    assert signed_transaction['signatures']
    assert len(signed_transaction['signatures']) == 1

    response = client.post('/validate-transaction', json=signed_transaction)
    assert response.status_code == 200

    response = client.post('/run-updater')
    assert response.status_code == 200

    return tcode
#    return signed_transaction['transaction']['trans_code']

def test_read_main():
    custodian_wallet = {
        "address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==",
        "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="
    }

    wallet1 = create_wallet()
    wallet2 = create_wallet()
    wallet3 = create_wallet()
    print("created wallets with addresses, ",wallet1['address']," and ",wallet2['address'])

    token2 = create_token(wallet2, custodian_wallet, 1000)
    token3 = create_token(wallet3, custodian_wallet, 2000)
    print("tokens created")

    ts = time.mktime(datetime.datetime.now().timetuple())
    due_date = ts + 120
    tcode = str(round(random.random()*1000,0))
    signatories = {"setup":wallet1['address'],"deploy":wallet1['address'],"make_repayment":wallet1['address']}
    contractspecs = {
                    "tokencode":token2,
                    "loanamount":500,
                    "repayment": 600,
                    "due_date": due_date,
                    "sec_token_code": token3,
                    "sec_token_amount": 1000,
                    "borrowerwallet": wallet1['address'],
                    "lenderwallet": wallet2['address'],
                    "secproviderwallet": wallet3['address']
                    }
    address = create_contract(wallet1, signatories, contractspecs)
    print(address)

    txdeploy = call_contract(address,"deploy",wallet1,params={"sender":wallet1['address']})
    print("got a tx of deployment as ", txdeploy)
    
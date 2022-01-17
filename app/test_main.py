from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


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

    custodian_wallet = {"address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
                        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==", "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="}

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


def create_token(wallet, custodian_wallet):
    response = client.post('/add-token', json={
        "token_name": "NEWTOKEN",
        "tokencode" : "",
        "token_type": "string",
        "first_owner": wallet['address'],
        "custodian": custodian_wallet['address'],
        "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
        "amount_created": 8888,
        "value_created": 1000,
        "disallowed_regions": [],
        "is_smart_contract_token": False,
        "token_attributes": {}
    })

    assert response.status_code == 200
    unsigned_transaction = response.json()
    assert unsigned_transaction['transaction']
    assert len(unsigned_transaction['signatures']) == 0

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

    tokens = state['tokens']
    token_in_state = next(
        x for x in tokens if x['parent_transaction_code'] == signed_transaction['transaction']['trans_code'])
    assert token_in_state

    balances = state['balances']
    balance = next(x for x in balances if x['wallet_address'] ==
                   wallet['address'] and x['tokencode'] == token_in_state['tokencode'])
    assert balance
    assert balance['balance'] == 8888

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

def test_read_main():
    custodian_wallet = {
        "address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",
        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==",
        "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="
    }

    wallet1 = create_wallet()
    wallet2 = create_wallet()

    token1 = create_token(wallet1, custodian_wallet)
    token2 = create_token(wallet2, custodian_wallet)

    create_transfer(wallet1, wallet2, token1, token2)

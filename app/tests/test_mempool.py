import time
import sqlite3

from ..codes.fs.mempool_manager import get_mempool_transaction
from ..codes.db_updater import update_wallet_token_balance
from fastapi.testclient import TestClient
from ..ntypes import NUSD_TOKEN_CODE
from ..constants import NEWRL_DB
from ..nvalues import TREASURY_WALLET_ADDRESS
from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)

init_newrl()


def test_get_transaction():
    mempool_transaction = get_mempool_transaction('123')
    assert mempool_transaction is None
    
    transaction = create_transaction(2)
    mempool_transaction = get_mempool_transaction(transaction['transaction']['trans_code'])
    assert mempool_transaction


def create_transaction(fee):
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

    unsigned_transaction['transaction']['fee'] = fee
    unsigned_transaction['transaction']['currency'] = NUSD_TOKEN_CODE

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

    return signed_transaction

import time
from fastapi.testclient import TestClient
from ..migrations.init import init_newrl

from ..main import app

client = TestClient(app)

init_newrl()


def check_newrl_wallet_balance(wallet_address, _balance):
    response = client.post('/get-balance', json={
        "balance_type": "TOKEN_IN_WALLET",
        "token_code": 'NWRL',
        "wallet_address": wallet_address
    })
    assert response.status_code == 200
    balance = response.json()['balance']
    assert balance == _balance


def test_mining_reward():
    response = client.get("/get-node-wallet-address")
    assert response.status_code == 200
    wallet = response.json()
    wallet_address = wallet['wallet_address']
    assert wallet_address

    check_newrl_wallet_balance(wallet_address, None)

    response = client.post('/run-updater')
    assert response.status_code == 200
    check_newrl_wallet_balance(wallet_address, 1000)
    
    time.sleep(2)
    response = client.post('/run-updater')
    assert response.status_code == 200
    check_newrl_wallet_balance(wallet_address, 1000)
    
    time.sleep(5)
    response = client.post('/run-updater')
    assert response.status_code == 200
    check_newrl_wallet_balance(wallet_address, 2000)
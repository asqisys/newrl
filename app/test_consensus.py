from fastapi.testclient import TestClient

from .main import app
from .codes.validator import validate_block, validate_receipt_signature
from .codes.signmanager import sign_object

client = TestClient(app)


test_wallet = {
    "public": "wTxCEIm7oaKrYmmWIaeEcd4B49DsHb+D4VilmzhQZJCEmhT1XMFa/WmWoyBK3SRDuNGc9iOYdRBBCfeE0esH6A==",
    "private": "erMsIsopb9N6MYnDxvWtC+iaNb4PmQTY72D3jM5+lFE=",
    "address": "0x08a04d6f6a90248df7c392083c8eb52bba929597"
}


def test_validate_block_receipt():
    receipt_data = {
        "block_index": 241,
        "block_hash": "0000fd83acfc2f42f07493b8711d4f7fffa75333e3eece24c0d3b55c4df7b7e2",
        "vote": 1
    }

    receipt = {
        "data": receipt_data,
        "public_key": test_wallet["public"],
        "signature": sign_object(test_wallet["private"], receipt_data)
    }

    assert validate_receipt_signature(receipt) is True

    # Test receive receipt via API as well
    response = client.post("/receive-receipt", json={'receipt': receipt})
    print(response.text)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'SUCCESS'


def test_block_validation_success():
    block_data = {
        "index": 241,
        "timestamp": "2021-09-21 10:23:35.077991",
        "proof": 17672,
        "text": {
            "transactions": [
                {
                    "timestamp": "2021-09-21 10:23:34.861279",
                    "trans_code": "9258f94aa73746c9f39eefe192e6ac02d804cf1a",
                    "type": 4,
                    "currency": "INR",
                    "fee": 0.0,
                    "descr": "",
                    "valid": 1,
                    "specific_data": {
                        "asset1_code": 2,
                        "asset2_code": 7,
                        "wallet1": "0x308c4f49f25dd2213fabe814b82dd0797ef4fcf2",
                        "wallet2": "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
                        "asset1_number": 40152,
                        "asset2_number": 3
                    }
                }
            ],
            "signatures": [
                [
                    {
                        "wallet_address": "0x308c4f49f25dd2213fabe814b82dd0797ef4fcf2",
                        "msgsign": "5Zzbdwwgs987Jmd6UYmOw6a/YdcLWuc6i2CeijOCK89+4kKD/ykkU09/8XoTeTBi2UKAS0BIZJmi2N+2t04pQQ=="
                    },
                    {
                        "wallet_address": "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
                        "msgsign": "YssOvWMxJZsbrppfgRePKYAZy9R6DacOwfEypNKiCBiMKYKVfLQPHzcROCX4aBCjccNt36xol+9cORrc2Jw8og=="
                    }
                ]
            ]
        },
        "previous_hash": "00007f86fcdcfabc4a7b1d825abb006b381eca375e223f2b036f1f706053c8c0"
    }

    block_signature = {
        "public_key": test_wallet["public"],
        "msgsign": sign_object(test_wallet["private"], block_data)
    }
    receipt_data = {
        "block_index": 241,
        "block_hash": "0000fd83acfc2f42f07493b8711d4f7fffa75333e3eece24c0d3b55c4df7b7e2",
        "vote": 1
    }
    block = {
        "index": 241,
        "hash": "0000fd83acfc2f42f07493b8711d4f7fffa75333e3eece24c0d3b55c4df7b7e2",
        "data": block_data,
        "signature": block_signature,
        "receipts": [
            {
                "data": receipt_data,
                "public_key": test_wallet["public"],
                "signature": sign_object(test_wallet["private"], receipt_data)
            },
            {
                "data": receipt_data,
                "public_key": test_wallet["public"],
                "signature": sign_object(test_wallet["private"], receipt_data)
            }
        ]
    }

    # assert validate_block(block) is True

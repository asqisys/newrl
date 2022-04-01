import requests

# NODE_URL = 'http://testnet.newrl.net:8182'
# WALLET = {"public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==","private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=","address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}

# NODE_URL = 'http://testnet.newrl.net:8090'
# WALLET = {"address": "0xc29193dbab0fe018d878e258c93064f01210ec1a","public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==","private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="}


NODE_URL = 'http://testnet.newrl.net:8090'
WALLET = {
  "public": "pEeY8E9fdKiZ3nJizmagKXjqDSK8Fz6SAqqwctsIhv8KctDfkJlGnSS2LUj/Igk+LwAl91Y5pUHZTTafCosZiw==",
  "private": "x1Hp0sJzfTumKDqBwPh3+oj/VhNncx1+DLYmcTKHvV0=",
  "address": "0x6e206561a7018d84b593c5e4788c71861d716880"
}

def add_wallet(public_key):
  add_wallet_request = {
    "custodian_address": WALLET['address'],
    "ownertype": "1",
    "jurisdiction": "910",
    "kyc_docs": [
  {
    "type": 1,
    "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401"
  }
    ],
    "specific_data": {},
    "public_key": public_key
  }

  response = requests.post(NODE_URL + '/add-wallet', json=add_wallet_request)

  unsigned_transaction = response.json()

  response = requests.post(NODE_URL + '/sign-transaction', json={
  "wallet_data": WALLET,
  "transaction_data": unsigned_transaction
  })

  signed_transaction = response.json()

  # print('signed_transaction', signed_transaction)
  print('Sending wallet add transaction to chain')
  response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
  print('Got response from chain\n', response.text)
  assert response.status_code == 200

public_key = input('Enter public key[leave blank to create new key pair]: ')

if public_key == '':
  response = requests.get(NODE_URL + '/generate-wallet-address')
  wallet = response.json()
  print('New wallet\n', wallet, '\n')
  public_key = wallet['public']

add_wallet(public_key)

import requests

# NODE_URL = 'http://testnet.newrl.net:8182'
NODE_URL = 'http://testnet.newrl.net:8090'
# NODE_URL = 'http://newrl.net:8090'
# WALLET = {    "public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==",    "private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=",    "address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}
WALLET = {        "address": "0xc29193dbab0fe018d878e258c93064f01210ec1a",        "public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==",        "private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="    }

token_code = input('Enter token code: ')
amount = input('Issue amount: ')
first_owner = input('First owner[c for custodian]: ')

if first_owner == 'c':
  first_owner = WALLET['address']

add_wallet_request = {
  "token_name": token_code,
  "token_code": token_code,
  "token_type": "1",
  "first_owner": first_owner,
  "custodian": WALLET['address'],
  "legal_doc": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401",
  "amount_created": amount,
  "value_created": amount,
  "disallowed_regions": [],
  "is_smart_contract_token": False,
  "token_attributes": {}
}

response = requests.post(NODE_URL + '/add-token', json=add_wallet_request)

unsigned_transaction = response.json()

response = requests.post(NODE_URL + '/sign-transaction', json={
    "wallet_data": WALLET,
    "transaction_data": unsigned_transaction
})

signed_transaction = response.json()

print('signed_transaction', signed_transaction)
response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
print(response.text)
print(response.status_code)
assert response.status_code == 200

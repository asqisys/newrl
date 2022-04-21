import requests

NODE_URL = 'http://18.208.160.119:8182'
# NODE_URL = 'http://44.203.127.164:8182'


last_block = requests.get(NODE_URL + '/get-last-block-index').text
last_block = int(last_block)

blocks = requests.post(NODE_URL + '/get-blocks', json={
  "block_indexes": list(range(1, last_block + 1))
}).json()

previous_hash = "0"

for block in blocks:
  print(block['block_index'])
  if block['previous_hash'] != previous_hash:
    print('Chain invalid from index', block['block_index'])
  previous_hash = block['hash']

print('Chain is valid')
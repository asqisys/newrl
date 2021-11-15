import json
import sqlite3


con = sqlite3.connect('../newrl.db')

cur = con.cursor()

with open('../state.json', 'r') as read_file:
  state_data = json.load(read_file)
  print(state_data)

for wallet in state_data['all_wallets']:
  doc_hash_1 = wallet['kyc_doc_hashes'][0] if len(wallet['kyc_doc_hashes']) > 0 else ''
  doc_hash_2 = wallet['kyc_doc_hashes'][1] if len(wallet['kyc_doc_hashes']) > 1 else ''
  db_wallet_data = (wallet['wallet_address'], wallet['wallet_public'], wallet['custodian_wallet'], doc_hash_1, doc_hash_2, wallet['ownertype'], wallet['jurisd'])
  cur.execute(f'''INSERT OR IGNORE INTO wallets
					(wallet_address, wallet_public, custodian_wallet, kyc_doc1_hash, kyc_doc2_hash, ownertype, jurisdiction)
					VALUES (?, ?, ?, ?, ?, ?, ?)''', db_wallet_data)

for token in state_data['all_tokens']:
  token_attributes = json.dumps(token['token_attributes']) if 'token_attributes' in token else ''
  db_token_data = (token['tokencode'], token['tokenname'], token['tokentype'], token['first_owner'], token['custodian'], token['legaldochash'], token['amount_created'], token['value_created'], token['sc_flag'], token_attributes)
  cur.execute(f'''INSERT OR IGNORE INTO tokens
  (tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, amount_created, value_created, sc_flag, token_attributes)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', db_token_data)

for balance in state_data['all_balances']:
  db_balance_data = (balance['wallet_address'], balance['tokencode'], balance['balance'])
  cur.execute(f'''INSERT OR REPLACE INTO balances
      (wallet_address, tokencode, balance) VALUES (?, ?, ?)''', db_balance_data)

con.commit()
con.close()
import sqlite3

con = sqlite3.connect('newrl.db')

cur = con.cursor()

# # Create table
# cur.execute('''
#                 CREATE TABLE wallets
#                 (wallet_address text, 
#                 wallet_public text,
#                 wallet_private text,
#                 custodian_wallet text,
#                 kyc_doc1_hash text,
#                 kyc_doc2_hash text,
#                 ownertype integer,
#                 jurisdiction integer)
#                 ''')

# # Insert a row of data
# cur.execute('''INSERT INTO wallets VALUES (
#     "0xc9192bbb51f7ced62b9b42bd65f22aafa67387fc",
#     "3rpV/+GcKJpyGfZyg+eXNYcXaBLWzIVs/9na054Z62easzuOcUp8ZRIoYZnx9T/243n94YCEkgY7tZo88l3Ezg==",
#     "Aeqb0lXOqFJRoVuFsWqstHR39VjUXSo6ggxNspT3zwY",
#     "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
#     "eda5b21da2c4ec8d4bbb1d84481cc8570f8d439a2e528b6c700c262d999d88c4",
#     "5762d4dd23caec4d917e3b711871959ab7a5e3e5ec94ad0bc96638e4cd18023d",
#     1,
#     910
# )''')

for row in cur.execute('SELECT * FROM wallets'):
        print(row)

# Save (commit) the changes
# con.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()
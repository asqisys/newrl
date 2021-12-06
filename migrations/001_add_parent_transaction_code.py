import sqlite3

con = sqlite3.connect('../newrl.db')

cur = con.cursor()

cur.execute("ALTER TABLE tokens ADD COLUMN parent_transaction_code text")

con.commit()
con.close
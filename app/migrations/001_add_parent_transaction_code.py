import sqlite3

from ..constants import NEWRL_DB

con = sqlite3.connect(NEWRL_DB)

cur = con.cursor()

cur.execute("ALTER TABLE tokens ADD COLUMN parent_transaction_code text")

con.commit()
con.close
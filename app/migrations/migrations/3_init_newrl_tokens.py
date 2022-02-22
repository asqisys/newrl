import sqlite3

from ...constants import NEWRL_DB

FOUNDATION_WALLET = '0xc29193dbab0fe018d878e258c93064f01210ec1a'
ASQI_WALLET = '0x20513a419d5b11cd510ae518dc04ac1690afbed6'
FOUNDATION_PUBLIC_KEY = 'sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg=='
ASQI_PUBLIC_KEY = 'PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg=='

FOUNDATION_RESERVE = 1500000000

def migrate():
    init_newrl_tokens()

def init_newrl_tokens():
    """Initialise NWRL tokens and pay the foundation"""
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()

    credit_wallet(cur, ASQI_WALLET, FOUNDATION_RESERVE)
    credit_wallet(cur, FOUNDATION_WALLET, FOUNDATION_RESERVE)

    con.commit()
    con.close()


def credit_wallet(cur, wallet, amount):
    query_params = (
            'NWRL',
            'Newrl',
            '1',
            wallet,
            '00000',
            amount,
            False,
            '0000',
            0,
            {}
        )
    cur.execute(f'''INSERT OR IGNORE INTO tokens
        (tokencode, tokenname, tokentype, first_owner, custodian, 
        amount_created, sc_flag, parent_transaction_code, tokendecimal, token_attributes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)
    
    cur.execute(f'''INSERT OR IGNORE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet, 'NWRL', amount))
    

if __name__ == '__main__':
    # migrate()
    pass

import sqlite3

p2p_db_path = 'newrl_p2p.db'

def clear_db():
    con = sqlite3.connect(p2p_db_path)
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS peers')
    con.commit()
    con.close()

def init_db():
    con = sqlite3.connect(p2p_db_path)
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS peers
                    (address text NOT NULL PRIMARY KEY)
                    ''')

    con.commit()
    con.close()


def get_peers(requester_address=None):
    peers = []
    con = sqlite3.connect(p2p_db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    try:
        peer_cursor = cur.execute('SELECT * FROM peers').fetchall()
        peers = [dict(ix) for ix in peer_cursor]
    except sqlite3.OperationalError as e:
        init_db()
    if requester_address:
        add_peer(requester_address)
    return peers


def add_peer(peer_address):
    peer_address = str(peer_address)

    if peer_address == '127.0.0.1':
        return
        
    con = sqlite3.connect(p2p_db_path)
    cur = con.cursor()
    try:
        peer_cursor = cur.execute('INSERT INTO peers(address) VALUES(?)', (peer_address, ))
        con.commit()
    except Exception as e:
        print(e)
        return False
    con.close()
    return True


def clear_peers():
    con = sqlite3.connect(p2p_db_path)
    cur = con.cursor()
    try:
        cur.execute('DELETE FROM peers')
        con.commit()
    except Exception as e:
        print(e)
        return False
    con.close()
    return True

if __name__ == '__main__':
    p2p_db_path = '../' + p2p_db_path
    clear_db()
    init_db()

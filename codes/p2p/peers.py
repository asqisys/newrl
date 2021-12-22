import sqlite3

import requests

from codes.constants import BOOTSTRAP_NODES

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
                    (id text NOT NULL PRIMARY KEY,
                    address text NOT NULL 
                    )
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
        register_me_with_them(peer_address)
        peer_cursor = cur.execute('INSERT INTO peers(id, address) VALUES(?, ?)', (peer_address, peer_address, ))
        con.commit()
    except Exception as e:
        print(e)
        return False
    con.close()
    return True


def remove_peer(peer_id):
    con = sqlite3.connect(p2p_db_path)
    cur = con.cursor()
    try:
        cur.execute('DELETE FROM peers where id = ?', (peer_id, ))
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

def init_bootstrap_nodes():
    print(f'Initiating node discovery from bootstrap nodes: {BOOTSTRAP_NODES}')
    # clear_peers()
    clear_db()
    init_db()

    for node in BOOTSTRAP_NODES:
        add_peer(node)
        response = requests.get('http://' + node + ':8092/get-peers')
        their_peers = response.json()
        print(f'Peers from node {node} : {their_peers}')
        for their_peer in their_peers:
            add_peer(their_peer['address'])
    
    my_peers = get_peers()

    for peer in my_peers:
        address = peer['address']
        try:
            response = register_me_with_them(address)
            if response.status_code != 200:
                remove_peer(peer)
        except Exception as e:
            print(f'Peer unreachable, deleting: {peer}')
            remove_peer(peer['address'])


def register_me_with_them(address):
    response = requests.post('http://' + address + ':8092/add-peer')

if __name__ == '__main__':
    p2p_db_path = '../' + p2p_db_path
    clear_db()
    init_db()

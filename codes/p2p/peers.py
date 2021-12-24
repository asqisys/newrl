import sqlite3

import requests
import socket

from codes.constants import BOOTSTRAP_NODES, REQUEST_TIMEOUT

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
    # if requester_address:
    #     add_peer(requester_address)
    return peers


async def add_peer(peer_address):
    peer_address = str(peer_address)

    if peer_address == '127.0.0.1':
        return
        
    con = sqlite3.connect(p2p_db_path)
    cur = con.cursor()
    try:
        # register_me_with_them(peer_address)
        peer_cursor = cur.execute('INSERT INTO peers(id, address) VALUES(?, ?)', (peer_address, peer_address, ))
        con.commit()
    except Exception as e:
        print(e)
    con.close()
    return {'address': peer_address}


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

async def init_bootstrap_nodes():
    print(f'Initiating node discovery from bootstrap nodes: {BOOTSTRAP_NODES}')
    # clear_peers()
    clear_db()
    init_db()

    my_address = await get_my_address()
    for node in BOOTSTRAP_NODES:
        if socket.gethostbyname(node) == my_address:
            continue
        await add_peer(node)
        try:
            response = requests.get('http://' + node + ':8092/get-peers', timeout=REQUEST_TIMEOUT)
            their_peers = response.json()
        except Exception as e:
            their_peers = []
            print('Error getting nodes.', e)
        print(f'Peers from node {node} : {their_peers}')
        for their_peer in their_peers:
            await add_peer(their_peer['address'])
    
    my_peers = get_peers()

    for peer in my_peers:
        address = peer['address']
        if socket.gethostbyname(address) == my_address:
            continue
        try:
            if address != my_address:
                response = await register_me_with_them(address)
        except Exception as e:
            print(f'Peer unreachable, deleting: {peer}')
            remove_peer(peer['address'])
    return True


async def register_me_with_them(address):
    response = requests.post('http://' + address + ':8092/add-peer', timeout=REQUEST_TIMEOUT)
    return response.json()

async def update_peers():
    my_peers = get_peers()
    my_address = await get_my_address()

    for peer in my_peers:
        address = peer['address']
        if socket.gethostbyname(address) == my_address:
            continue
        try:
            response = requests.post(
                'http://' + address + ':8092/update-software?update_peers=false&bootstrap_again=false',
                timeout=REQUEST_TIMEOUT
            )
            assert response.status_code == 200
            assert response.json()['status'] == 'SUCCESS'
        except Exception as e:
            print('Error updating software on peer', str(e))
    return True

async def get_my_address():
    return requests.get('https://api.ipify.org?format=json').json()['ip']

if __name__ == '__main__':
    p2p_db_path = '../' + p2p_db_path
    clear_db()
    init_db()

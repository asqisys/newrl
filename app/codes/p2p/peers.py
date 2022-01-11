import logging
import sqlite3
import requests
import socket
import subprocess
from app.migrations.init import init_newrl
from ...constants import BOOTSTRAP_NODES, REQUEST_TIMEOUT, NEWRL_P2P_DB, NEWRL_PORT


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_peer_db():
    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS peers')
    con.commit()
    con.close()

def init_peer_db():
    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS peers
                    (id text NOT NULL PRIMARY KEY,
                    address text NOT NULL 
                    )
                    ''')
    # Todo - link node to a person and add record in the node db
    con.commit()
    con.close()


def get_peers():
    peers = []
    con = sqlite3.connect(NEWRL_P2P_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    peer_cursor = cur.execute('SELECT * FROM peers').fetchall()
    peers = [dict(ix) for ix in peer_cursor]
    return peers


async def add_peer(peer_address):
    peer_address = str(peer_address)

    if peer_address == '127.0.0.1':
        return {'address': peer_address, 'status': 'FAILURE'}

    con = sqlite3.connect(NEWRL_P2P_DB)
    cur = con.cursor()
    try:
        logger.info('Adding peer %s', peer_address)
        # await register_me_with_them(peer_address)
        cur.execute('INSERT INTO peers(id, address) VALUES(?, ?)', (peer_address, peer_address, ))
        con.commit()
    except Exception as e:
        logger.info('Did not add peer %s', peer_address)
        return {'address': peer_address, 'status': 'FAILURE', 'reason': str(e)}
    con.close()
    return {'address': peer_address, 'status': 'SUCCESS'}


def remove_peer(peer_id):
    con = sqlite3.connect(NEWRL_P2P_DB)
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
    con = sqlite3.connect(NEWRL_P2P_DB)
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
    # clear_peer_db()
    init_peer_db()

    my_address = await get_my_address()
    for node in BOOTSTRAP_NODES:
        if socket.gethostbyname(node) == my_address:
            continue
        logger.info(f'Boostrapping from node {node}')
        await add_peer(node)
        try:
            response = requests.get('http://' + node + f':{NEWRL_PORT}/get-peers', timeout=REQUEST_TIMEOUT)
            their_peers = response.json()
        except Exception as e:
            their_peers = []
            print('Error getting nodes.', e)
        print(f'Peers from node {node} : {their_peers}')
        for their_peer in their_peers:
            await add_peer (their_peer['address'])
    
    my_peers = get_peers()

    for peer in my_peers:
        address = peer['address']
        if socket.gethostbyname(address) == my_address:
            continue
        try:
            response = await register_me_with_them(address)
        except Exception as e:
            print(f'Peer unreachable, deleting: {peer}')
            remove_peer(peer['address'])
    return True


async def register_me_with_them(address):
    logger.info(f'Registering me with node {address}')
    response = requests.post('http://' + address + f':{NEWRL_PORT}/add-peer', timeout=REQUEST_TIMEOUT)
    return response.json()

async def update_peers():
    my_peers = get_peers()
    my_address = await get_my_address()

    for peer in my_peers:
        address = peer['address']
        logger.info('Updating peers: %s', address)
        if socket.gethostbyname(address) == my_address:
            continue
        try:
            response = requests.post(
                'http://' + address + f':{NEWRL_PORT}/update-software',
                timeout=REQUEST_TIMEOUT
            )
            assert response.status_code == 200
            assert response.json()['status'] == 'SUCCESS'
        except Exception as e:
            print('Error updating software on peer', str(e))
    return True

async def get_my_address():
    return requests.get('https://api.ipify.org?format=json').json()['ip']


async def update_software(propogate):
    "Update the client software from repo"
    logger.info('Getting latest code from repo')
    subprocess.call(["git", "pull"])
    init_newrl()
    if propogate is True:
        logger.info('Propogaring update request to network')
        await update_peers()
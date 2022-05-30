import sqlite3
import requests
import socket

from ...constants import NEWRL_P2P_DB


def get_peers():
    peers = []
    con = sqlite3.connect(NEWRL_P2P_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    peer_cursor = cur.execute('SELECT * FROM peers').fetchall()
    peers = [dict(ix) for ix in peer_cursor]
    return peers


def get_my_address():
    return requests.get('https://api.ipify.org?format=json').json()['ip']


def is_my_address(address):
    my_address = get_my_address()
    if socket.gethostbyname(address) == my_address:
        return True
    return False

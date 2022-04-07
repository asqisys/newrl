from random import randint
import sys
import threading
import uvicorn
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request

from app.codes.chainscanner import download_chain, download_state
from app.codes.clock.global_time import get_time_stats
from app.codes.fs.mempool_manager import clear_mempool
from app.codes.p2p.peers import add_peer, clear_peers, get_peers, update_software
from app.codes.p2p.sync_chain import get_blocks, get_last_block_index, sync_chain_from_node, sync_chain_from_peers
from app.codes.p2p.sync_mempool import list_mempool_transactions, sync_mempool_transactions
from app.codes.updater import TIMERS
from app.codes.utils import get_last_block_hash
from app.constants import SOFTWARE_VERSION
from app.migrations.init_db import clear_db, init_db, revert_chain
from app.codes.p2p.peers import call_api_on_peers
from app.codes.auth.auth import get_node_wallet_public
from app.codes.minermanager import get_miner_info

router = APIRouter()

p2p_tag = 'System'


@router.get("/get-node-info", tags=[p2p_tag])
def get_node_info():
    last_block = get_last_block_hash()
    last_block_index = last_block['index']
    node_info = {
        'software_version': SOFTWARE_VERSION,
        'wallet': get_node_wallet_public(),
        'time': get_time_stats(),
        'last_block': last_block,
        'miners': get_miner_info(),
        'peers': get_peers(),
        'recent_blocks': get_blocks(list(range(last_block_index - 10, last_block_index))),
        'mempool_transactions': list_mempool_transactions(),
    }
    return node_info


@router.get("/download-chain", tags=[p2p_tag])
def download_chain_api():
    return download_chain()


@router.get("/download-state", tags=[p2p_tag])
def download_state_api():
    return download_state()


@router.post("/sync-mempool-transactions", tags=[p2p_tag])
def sync_mempool_transactions_api():
    return sync_mempool_transactions()


@router.post("/sync-chain-from-node", tags=[p2p_tag])
def sync_chain_from_node_api(url: str = 'https://newrl-devnet1.herokuapp.com'):
    try:
        return sync_chain_from_node(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail='No more blocks')


@router.post("/sync-chain-from-peers", tags=[p2p_tag])
def sync_chain_from_peers_api():
    return sync_chain_from_peers()


@router.post("/sync-chain-from-peers", tags=[p2p_tag])
def sync_chain_from_peers_api():
    return sync_chain_from_peers()


@router.post("/clear-db-test-only", tags=[p2p_tag])
def clear_db_api():
    """ For testing only. To be removed. Clear and initialise a fresh db """
    clear_db()
    init_db()
    return True


@router.post("/clear-peers", tags=[p2p_tag])
def clear_peer_api(req: Request):
    return clear_peers()

@router.post("/clear-mempool", tags=[p2p_tag])
def clear_mempool_api(req: Request):
    return clear_mempool()


@router.post("/initiate-peer-connection", tags=[p2p_tag])
def initiate_peer_api(address: str):
    "Test only, used to first connect a client"
    return add_peer(address)


@router.post("/turn-off-mining-clock", tags=[p2p_tag])
def switch_mining_clock_api():
    global TIMERS

    if TIMERS['mining_timer'] is not None:
        print('Turning off mining clock')
        TIMERS['mining_timer'].cancel()
        return {'status': 'SUCCESS'}
    return {'status': 'FAILURE', 'message': 'Mining clock not running'}


@router.post("/revert-chain", tags=[p2p_tag])
def revert_chain_api(block_index: int, propogate: bool = False):
    revert_chain(block_index)
    if propogate:
        call_api_on_peers(f'/revert-chain?block_index={block_index}')
    return {'status': 'SUCCESS'}


@router.post("/update-software", tags=[p2p_tag])
def update_software_api(propogate: bool = False):
    # update_software(propogate)
    timer = threading.Timer(randint(30, 60), update_software, [propogate])
    timer.start()
    return {'status': 'SUCCESS'}

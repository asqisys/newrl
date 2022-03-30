from random import randint
import sys
import threading
import uvicorn
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request

from app.codes.chainscanner import download_chain, download_state, get_transaction
from app.codes.p2p.peers import add_peer, clear_peers, get_peers, update_software
from app.codes.p2p.sync_chain import get_blocks, get_last_block_index, receive_block, receive_receipt, sync_chain_from_node, sync_chain_from_peers
from app.codes.p2p.sync_mempool import get_mempool_transactions, list_mempool_transactions, sync_mempool_transactions
from app.constants import NEWRL_PORT
from app.migrations.init_db import clear_db, init_db, revert_chain
from app.codes.p2p.peers import call_api_on_peers
from .request_models import BlockAdditionRequest, BlockRequest, ReceiptAdditionRequest, TransactionAdditionRequest, TransactionsRequest
from app.codes.auth.auth import get_node_wallet_address, get_node_wallet_public
from app.codes.validator import validate as validate_transaction
from app.codes.minermanager import get_miner_info

router = APIRouter()

p2p_tag = 'p2p'

@router.get("/get-node-wallet-address", tags=[p2p_tag])
def api_get_node_wallet_address():
    return {'wallet_address': get_node_wallet_address()}


@router.post("/list-mempool-transactions", tags=[p2p_tag])
def list_mempool_transactions_api():
    return list_mempool_transactions()

@router.post("/get-mempool-transactions", tags=[p2p_tag])
def get_mempool_transactions_api(req: TransactionsRequest):
    return get_mempool_transactions(req.transaction_codes)

@router.post("/get-blocks", tags=[p2p_tag])
def get_mempool_transactions_api(req: BlockRequest):
    return get_blocks(req.block_indexes)

@router.post("/receive-transaction", tags=[p2p_tag])
def receive_transaction_api(req: TransactionAdditionRequest):
    return validate_transaction(req.signed_transaction, propagate=False)

@router.post("/receive-block", tags=[p2p_tag])
def receive_block_api(req: BlockAdditionRequest):
    return receive_block(req.block)

@router.post("/receive-receipt", tags=[p2p_tag])
def receive_receipt_api(req: ReceiptAdditionRequest):
    if receive_receipt(req.receipt):
        return {'status': 'SUCCESS'}
    else:
        return {'status': 'FAILURE'}

@router.get("/get-last-block-index", tags=[p2p_tag])
def get_last_block_index_api():
    return get_last_block_index()

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

@router.get("/get-transaction", tags=[p2p_tag])
def get_transaction_api(transaction_code: str):
    return get_transaction(transaction_code)

@router.get("/download-chain", tags=[p2p_tag])
def download_chain_api():
    return download_chain()

@router.get("/download-chain", tags=[p2p_tag])
def download_chain_api():
    return download_chain()

@router.get("/download-state", tags=[p2p_tag])
def download_state_api():
    return download_state()

@router.post("/clear-db-test-only", tags=[p2p_tag])
def clear_db_api():
    """ For testing only. To be removed. Clear and initialise a fresh db """
    clear_db()
    init_db()
    return True

@router.get("/get-peers", tags=[p2p_tag])
def get_peers_api():
    return get_peers()

@router.get("/get-miners", tags=[p2p_tag])
def get_miners_api():
    return get_miner_info()

@router.post("/add-peer", tags=[p2p_tag])
def add_peer_api(req: Request):
    return add_peer(req.client.host)

@router.post("/clear-peers", tags=[p2p_tag])
def clear_peer_api(req: Request):
    return clear_peers()

@router.post("/initiate-peer-connection", tags=[p2p_tag])
def initiate_peer_api(address: str):
    "Test only, used to first connect a client"
    return add_peer(address)

@router.post("/revert-chain", tags=[p2p_tag])
def revert_chain_api(block_index: int, propogate: bool = False):
    revert_chain(block_index)
    if propogate:
        call_api_on_peers(f'/revert-chain?block_index={block_index}')
    return {'status': 'SUCCESS'}

@router.post("/update-software", tags=[p2p_tag])
def update_software_api(propogate: bool = False):
    # update_software(propogate)
    timer = threading.Timer(randint(5, 10), update_software, [propogate])
    timer.start()
    return {'status': 'SUCCESS'}


@router.get("/get-node-info", tags=[p2p_tag])
def get_miners_api():
    last_block = get_last_block_index()
    node_info = {
        'wallet': get_node_wallet_public(),
        'miners': get_miner_info(),
        'peers': get_peers(),
        'last_block': last_block,
        'recent_blocks': get_blocks(list(range(last_block - 10, last_block))),
        'mempool_transactions': list_mempool_transactions()
    }
    return node_info

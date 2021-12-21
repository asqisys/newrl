from starlette.requests import Request
import uvicorn
from fastapi import FastAPI
from codes.chainscanner import download_chain, download_state, get_transaction
from codes.p2p.peers import add_peer, clear_peers, get_peers
from codes.p2p.sync_chain import get_block, get_blocks, get_last_block_index, sync_chain_from_node

from codes.p2p.sync_mempool import get_mempool_transactions, list_mempool_transactions, sync_mempool_transactions
from migrations.init_db import clear_db, init_db
from p2p_request_models import TransactionsRequest


app = FastAPI(
    title="The Newrl APIs",
    description="The p2p"
)

p2p_tag = 'p2p'

@app.post("/list-mempool-transactions", tags=[p2p_tag])
async def list_mempool_transactions_api():
    return list_mempool_transactions()

@app.post("/get-mempool-transactions", tags=[p2p_tag])
async def get_mempool_transactions_api(req: TransactionsRequest):
    return get_mempool_transactions(req.transaction_codes)

@app.post("/get-blocks", tags=[p2p_tag])
async def get_mempool_transactions_api(req: TransactionsRequest):
    return get_blocks(req.transaction_codes)

@app.get("/get-last-block-index", tags=[p2p_tag])
async def get_last_block_index_api():
    return get_last_block_index()

@app.post("/sync-mempool-transactions", tags=[p2p_tag])
async def sync_mempool_transactions_api():
    return sync_mempool_transactions()

@app.post("/sync-chain-from-node", tags=[p2p_tag])
async def sync_chain_from_node_api(url: str = 'https://newrl-devnet1.herokuapp.com'):
    return sync_chain_from_node(url)

@app.get("/get-transaction", tags=[p2p_tag])
async def get_transaction_api(transaction_code: str):
    return get_transaction(transaction_code)

@app.get("/download-chain", tags=[p2p_tag])
async def download_chain_api():
    return download_chain()

@app.get("/download-state", tags=[p2p_tag])
async def download_state_api():
    return download_state()

@app.post("/clear-db-test-only", tags=[p2p_tag])
async def clear_db_api():
    """ For testing only. To be removed. Clear and initialise a fresh db """
    clear_db()
    init_db()
    return True

@app.get("/get-peers", tags=[p2p_tag])
async def get_peers_api():
    return get_peers()

@app.post("/add-peer", tags=[p2p_tag])
async def get_peer_api(req: Request):
    return add_peer(req.client.host)

@app.post("/clear-peers", tags=[p2p_tag])
async def clear_peer_api(req: Request):
    return clear_peers()


if __name__ == "__main__":
    uvicorn.run("p2p_main:app", host="0.0.0.0", port=8092, reload=True)
import uvicorn
from fastapi import FastAPI
from codes.chainscanner import download_chain, download_state, get_transaction
from codes.p2p.sync_chain import get_block, get_blocks, get_last_block_index, sync_chain_from_node

from codes.p2p.sync_mempool import get_mempool_transactions, list_mempool_transactions, sync_mempool_transactions
from migrations.init_db import clear_db, init_db
from p2p_request_models import TransactionsRequest


app = FastAPI(
    title="The Newrl APIs",
    description="The p2p"
)


@app.post("/list-mempool-transactions")
async def list_mempool_transactions_api():
    return list_mempool_transactions()

@app.post("/get-mempool-transactions")
async def get_mempool_transactions_api(req: TransactionsRequest):
    return get_mempool_transactions(req.transaction_codes)

@app.post("/get-blocks")
async def get_mempool_transactions_api(req: TransactionsRequest):
    return get_blocks(req.transaction_codes)

@app.get("/get-last-block-index")
async def get_last_block_index_api():
    return get_last_block_index()

@app.post("/sync-mempool-transactions")
async def sync_mempool_transactions_api():
    return sync_mempool_transactions()

@app.post("/sync-chain-from-node")
async def sync_chain_from_node_api(url: str = 'https://newrl-devnet1.herokuapp.com'):
    return sync_chain_from_node(url)

@app.get("/get-transaction")
async def get_transaction_api(transaction_code: str):
    return get_transaction(transaction_code)

@app.get("/download-chain")
async def download_chain_api():
    return download_chain()

@app.get("/download-state")
async def download_state_api():
    return download_state()

@app.post("/clear-db-test-only")
async def clear_db_api():
    """ For testing only. To be removed. Clear and initialise a fresh db """
    clear_db()
    init_db()
    return True

if __name__ == "__main__":
    uvicorn.run("p2p_main:app", host="0.0.0.0", port=8092, reload=True)
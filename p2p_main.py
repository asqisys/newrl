import uvicorn
from fastapi import FastAPI

from codes.p2p.sync_mempool import get_mempool_transactions, list_mempool_transactions, sync_mempool_transactions
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

@app.post("/sync-mempool-transactions")
async def sync_mempool_transactions_api():
    return sync_mempool_transactions()


if __name__ == "__main__":
    uvicorn.run("p2p_main:app", host="0.0.0.0", port=8092, reload=True)
import logging
import uvicorn
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

from app.codes.p2p.sync_chain import sync_chain_from_peers

from .constants import NEWRL_PORT
from .codes.p2p.peers import init_bootstrap_nodes, update_software

from .routers import blockchain
from .routers import p2p
from .routers import transport


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="The Newrl APIs",
    description="This page covers all the public APIs available at present in the Newrl blockchain platform."
)

app.include_router(blockchain.router)
app.include_router(p2p.router)
app.include_router(transport.router)

@app.on_event('startup')
async def app_startup():
    try:
        await init_bootstrap_nodes()
        sync_chain_from_peers()
        await update_software(propogate=False)
    except Exception as e:
        print('Bootstrap failed', str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=NEWRL_PORT, reload=True)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Newrl APIs",
        version="1.0",
        description="APIs for Newrl - the blockchain platform to tokenize assets - to invest, lend and pay on-chain.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "http://newrl.net/assets/img/icons/newrl_logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

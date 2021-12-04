import json
import logging

from fastapi.datastructures import UploadFile
from fastapi.params import File
import uvicorn
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

from codes.chainscanner import Chainscanner, download_chain, download_state
from codes.kycwallet import Walletmanager
from codes.tokenmanager import create_token_transaction
from codes.transfermanager import Transfermanager
from request_models import BalanceRequest, BalanceType, CreateTokenRequest, TransferRequest
from codes.utils import save_file_and_get_path
from codes.transactionmanager import Transactionmanager

from codes import validator
from codes import signmanager
from codes import updater

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="The Newrl APIs",
    description="This page covers all the public APIs available at present in the Newrl blockchain platform."
)


@app.post("/create-transfer")
async def create_transfer(transfer_request: TransferRequest):
    """Used to create a transfer file which can be signed and executed by /sign and /transfer respectively"""
    trandata = {
        "asset1_code": int(transfer_request.asset1_code),
        "asset2_code": int(transfer_request.asset2_code),
        "wallet1": transfer_request.wallet1_address,
        "wallet2": transfer_request.wallet2_address,
        "asset1_number": int(transfer_request.asset1_qty),
        "asset2_number": int(transfer_request.asset2_qty)
    }
#    if transfer_type.lower()=="type4":
#        type=4
#    if transfer_type.lower()=="type5":
#        type=5
    type = transfer_request.transfer_type
    fulltrandata = {
        "transaction": {
            "timestamp": "",
            "trans_code": "000000",
            "type": type,
            "currency": "INR",
            "fee": 0.0,
            "descr": "",
            "valid": 1,
            "block_index": 0,
            "specific_data": trandata
        },
        "signatures": []
    }
    with open("transfernew.json", 'w') as file:
        json.dump(fulltrandata, file)

    newtransfer = Transfermanager(transferfile="transfernew.json")
    newtransfer.loadandcreate(transferfile="transfernew.json")
#    with open("./transfernew.json","r") as tfile:
#        transferfile_path = save_file_and_get_path(tfile)
    transferfile = FileResponse(
        "transfernew.json", filename="transferfile.json")
    return transferfile


@app.post("/transfer")
async def transfer(transferfile: UploadFile = File(...)):
    """Execute a transaction from a given wallet file. Alternate to /create-transfer"""
    transferfile_path = save_file_and_get_path(transferfile)
    newtransfer = Transfermanager(transferfile=transferfile_path)
    newtransfer.loadandcreate(transferfile=transferfile_path)
    response_file = FileResponse(
        transferfile_path, filename="transfer_transaction.json")
    return response_file


@app.post("/add-wallet")
async def add_wallet_api(custodian_address: str = "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
                         ownertype: str = "1", jurisdiction: str = "910",
                         kyc1: UploadFile = File(...), kyc2: UploadFile = File(...)):
    """Add a new wallet under a specified custodian"""
    f1 = save_file_and_get_path(kyc1)
    f2 = save_file_and_get_path(kyc2)
    idfile = f1
    adfile = f2
    kyccust = "0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42"
    walletfile = "all_wallets.json"
    ownertype = 1
    jurisdiction = 910

    wm = Walletmanager(walletfile)
    files = []
    files.append(idfile)
    files.append(adfile)
    kycdocs = [1, 2]
    specific_data = []
    kyccust = kyccust
    transferfile, keysdata = wm.wallet_maker(
        kyccust, kycdocs, files, ownertype, jurisdiction, specific_data)
#	wm.kycdocslinker(files,kycdocs)
    with open(keysdata[0]['address'] + "_wallet.json", "w") as writefile:
        json.dump(keysdata, writefile)
    # wm.walletlistupdater()
    return FileResponse(transferfile, filename="add_wallet_transaction.json")


@app.post("/get-wallet-file")
async def get_wallet_file(transferfile: UploadFile = File(...)):
    """Returns the wallet file from the add_wallet_transaction.json"""
    f1 = save_file_and_get_path(transferfile)
    with open(f1, 'r+') as file:
        data = json.load(file)
        walletfile = data["transaction"]["specific_data"]["wallet_address"] + "_wallet.json"
    return FileResponse(walletfile, filename="walletfile.json")


@app.post("/sign")
async def sign(wallet_file: UploadFile = File(...), transactionfile: UploadFile = File(...)):
    """Custodian wallet file can be used to sign a transaction"""
    transactionfile_path = save_file_and_get_path(transactionfile)
    wallet_file = save_file_and_get_path(wallet_file)
    singed_transaction_file = signmanager.sign(
        wallet_file, transactionfile_path)
    return singed_transaction_file


@app.post("/validate")
async def validate(transactionfile: UploadFile = File(...)):
    """Validate a given transaction file if it's included in chain"""
    transactionfile_path = save_file_and_get_path(transactionfile)
    response = validator.validate(transactionfile_path)
    return {"status": "SUCCESS", "response": response}


@app.post("/create-token")
async def create_token(
    request: CreateTokenRequest
):
    token_data = {
        "tokencode": 0,
        "tokenname": request.token_name,
        "tokentype": request.token_type,
        "tokenattributes": request.token_attributes,
        "first_owner": request.first_owner,
        "custodian": request.custodian,
        "legaldochash": request.legal_doc,
        "amount_created": request.amount_created,
        "value_created": request.value_created,
        "disallowed": request.disallowed_regions,
        "sc_flag": request.is_smart_contract_token
    }
    try:
        token_create_transaction_filename = create_token_transaction(token_data)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    response_file = FileResponse(token_create_transaction_filename, filename="token_create_transaction.json")
    return response_file


@app.post("/run-updater", response_class=HTMLResponse)
async def run_updater():
    log = updater.run_updater()
    HTMLResponse(content=log, status_code=200)
    return log


@app.get("/download-chain")
async def download_chain_api():
    return download_chain()


@app.get("/download-state")
async def download_state_api():
    return download_state()


@app.post("/get-balance")
async def get_balance(req: BalanceRequest):
    chain_scanner = Chainscanner()
    if req.balance_type == BalanceType.TOKEN_IN_WALLET:
        balance = chain_scanner.getbaladdtoken(
            req.wallet_address, int(req.token_code))
    elif req.balance_type == BalanceType.ALL_TOKENS_IN_WALLET:
        balance = chain_scanner.getbalancesbyaddress(req.wallet_address)
    elif req.balance_type == BalanceType.ALL_WALLETS_FOR_TOKEN:
        balance = chain_scanner.getbalancesbytoken(int(req.token_code))
    return balance


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


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

from codes.chainscanner import Chainscanner
import json
from request_models import BalanceRequest, BalanceType, TransferRequest
from typing import Optional
from starlette.responses import FileResponse
from utils import save_file_and_get_path
from codes.transactionmanager import Transactionmanager
from codes.addwallet import add_wallet
from fastapi.datastructures import UploadFile
from fastapi.params import File
import uvicorn
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

from codes import validator
from codes import signmanager
from codes import updater
from codes import addtransfer
from codes import addtoken

app = FastAPI(
    title="The Newrl APIs",
    description="This page covers all the public APIs available at present in the Newrl blockchain platform."
)

@app.post("/create-transfer")
async def create_transfer(
    transfer_type,
    asset1_code,
    asset2_code,
    wallet1_address,
    wallet2_address,
    asset1_quantity,
    asset2_quantity
    ):
    trandata={
    "asset1_code":int(asset1_code), "asset2_code":int(asset2_code), "wallet1":wallet1_address, "wallet2":wallet2_address, "asset1_number":int(asset1_quantity),"asset2_number":int(asset2_quantity)
    }
#    if transfer_type.lower()=="type4":
#        type=4
#    if transfer_type.lower()=="type5":
#        type=5
    type=int(transfer_type)
    fulltrandata={"transaction":{"timestamp": "", "trans_code": "000000", "type":type, "currency": "INR", "fee": 0.0, "descr":"", "valid": 1, "block_index": 0, "specific_data": trandata},"signatures":[]}
    with open("data/tmp/transfernew.json", 'w') as file:
        json.dump(fulltrandata,file)

    transfer = addtransfer.create_transfer(transferfile="data/tmp/transfernew.json")
#    with open("./data/tmp/transfernew.json","r") as tfile:
#        transferfile_path = save_file_and_get_path(tfile)
    transferfile = FileResponse("data/tmp/transfernew.json", filename="transferfile.json")
    return transferfile

@app.post("/transfer")
async def transfer(transferfile: UploadFile = File(...)):
    transferfile_path = save_file_and_get_path(transferfile)
    transfer = addtransfer.create_transfer(transferfile=transferfile_path)
    response_file = FileResponse(transferfile_path, filename="transferfile.json")
    return response_file
    
@app.post("/add-wallet")
async def add_wallet_api(custodian_address: str = "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
    ownertype: str = "1", jurisdiction: str = "910",
    kyc1: UploadFile = File(...), kyc2: UploadFile = File(...)):
    f1 = save_file_and_get_path(kyc1)
    f2 = save_file_and_get_path(kyc2)
    transferfile = add_wallet(f1, f2, custodian_address)
    return FileResponse(transferfile, filename="transferfile.json")

@app.post("/get-wallet-file")
async def get_wallet_file(transferfile: UploadFile = File(...)):
    f1 = save_file_and_get_path(transferfile)
    with open(f1, 'r+') as file:
        data=json.load(file)
        walletfile = "data/wallets" + data["transaction"]["specific_data"]["wallet_address"] + "_wallet.json"
    return FileResponse(walletfile, filename="walletfile.json")

@app.post("/sign")
async def sign(wallet_file: UploadFile = File(...), transactionfile: UploadFile = File(...)):
    transactionfile_path = save_file_and_get_path(transactionfile)
    wallet_file = save_file_and_get_path(wallet_file)
    singed_transaction_file = signmanager.sign(wallet_file, transactionfile_path)
    return singed_transaction_file

@app.post("/validate")
async def validate(transactionfile: UploadFile = File(...)):
    transactionfile_path = save_file_and_get_path(transactionfile)
    response = validator.validate(transactionfile_path)
    return {"status": "SUCCESS", "response": response}

@app.post("/create-token")
async def create_token(
    token_name,
    token_type,
    first_owner,
    custodian,
    legal_doc,
    amount_created,
    value_created,
):
    tokendata={
    "tokencode": 0,"tokenname":token_name, "tokentype": token_type, "tokenattributes": {}, "first_owner": first_owner, "custodian": custodian,
    "legaldochash": legal_doc, "amount_created": int(amount_created), "value_created": int(value_created), "disallowed": [], "sc_flag": False
    }
    with open("data/tmp/tokennew.json", 'w') as file:
        json.dump(tokendata,file)
    transaction_file = addtoken.add_token("data/tmp/tokennew.json")
    return FileResponse(transaction_file, filename="transaction_file.json")


@app.post("/run-updater")
async def run_updater():
    log = updater.run_updater()
    return {"status": "SUCCESS", "log": log}

@app.get("/download-chain")
async def download_chain():
    return FileResponse("data/common/chain.json", filename="chain.json")

@app.get("/download-state")
async def download_state():
    return FileResponse("data/common/state.json", filename="state.json")

@app.post("/get-balance")
async def get_balance(req: BalanceRequest):
    chain_scanner = Chainscanner()
    if req.balance_type == BalanceType.TOKEN_IN_WALLET:
        balance = chain_scanner.getbaladdtoken(req.wallet_address, int(req.token_code))
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

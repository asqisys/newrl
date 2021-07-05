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
from fastapi import FastAPI

from codes import validator
from codes import signmanager
from codes import updater
from codes import addtransfer
from codes import addtoken

app = FastAPI()


@app.post("/validate")
async def validate(transactionfile: UploadFile = File(...)):
    transactionfile_path = save_file_and_get_path(transactionfile)
    response = validator.validate(transactionfile_path)
    return {"status": "SUCCESS", "response": response}
    
@app.post("/add-wallet")
async def validate(custodian_address: str = "0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
    ownertype: str = "1", jurisdiction: str = "910",
    kyc1: UploadFile = File(...), kyc2: UploadFile = File(...)):
    f1 = save_file_and_get_path(kyc1)
    f2 = save_file_and_get_path(kyc2)
    transferfile = add_wallet(f1, f2, custodian_address)
    return FileResponse(transferfile, filename="transferfile.json")

@app.post("/get-wallet-file")
async def validate(transferfile: UploadFile = File(...)):
    f1 = save_file_and_get_path(transferfile)
    with open(f1, 'r+') as file:
        data=json.load(file)
        walletfile = data["transaction"]["specific_data"]["wallet_address"] + "_wallet.json"
    return FileResponse(walletfile, filename="walletfile.json")

@app.post("/transfer")
async def transfer(transferfile: UploadFile = File(...)):
    transferfile_path = save_file_and_get_path(transferfile)
    transfer = addtransfer.create_transfer(transferfile=transferfile_path)
    response_file = FileResponse(transferfile_path, filename="transferfile.json")
    return response_file

@app.post("/sign")
async def sign(wallet_file: UploadFile = File(...), transactionfile: UploadFile = File(...)):
    transactionfile_path = save_file_and_get_path(transactionfile)
    wallet_file = save_file_and_get_path(wallet_file)
    singed_transaction_file = signmanager.sign(wallet_file, transactionfile_path)
    return singed_transaction_file

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
    "legaldochash": None, "amount_created": amount_created, "value_created": value_created, "disallowed": [], "sc_flag": false
    }
    with open("tokennew.json", 'w') as file:
        json.dump(tokendata,file)
    tokenfile_path = addtoken.add_token("tokennew.json")
    response_file = FileResponse(tokenfile_path, filename="newtoken.json")
    return response_file

@app.post("/run-updater")
async def run_updater():
    log = updater.run_updater()
    return {"status": "SUCCESS", "log": log}

@app.get("/download-chain")
async def download_chain():
    return FileResponse("chain.json", filename="chain.json")

@app.get("/download-state")
async def download_state():
    return FileResponse("state.json", filename="state.json")

@app.post("/get-balance")
async def get_balance(req: BalanceRequest):
    chain_scanner = Chainscanner()
    if req.balance_type == BalanceType.TOKEN_IN_WALLET:
        balance = chain_scanner.getbaladdtoken(req.wallet_address, req.token_code)
    elif req.balance_type == BalanceType.ALL_TOKENS_IN_WALLET:
        balance = chain_scanner.getbalancesbyaddress(req.wallet_address)
    elif req.balance_type == BalanceType.ALL_WALLETS_FOR_TOKEN:
        balance = chain_scanner.getbalancesbytoken(req.token_code)
    return balance


@app.post("/create-transfer")
async def create_transfer(req: TransferRequest):
    transferfile_path = save_file_and_get_path(None)
    transfer = addtransfer.create_transfer(transferfile=transferfile_path)
    response_file = FileResponse(transferfile_path, filename="transferfile.json")
    return transfer


if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


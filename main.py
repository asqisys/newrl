import json
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
async def validate(custodian_address: str = "0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42",
    kyc1: Optional[UploadFile] = File(None), kyc2: Optional[UploadFile] = File(None)):
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
    tokenfile_path = addtoken.add_token()
    response_file = FileResponse(tokenfile_path, filename="token.json")
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


if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


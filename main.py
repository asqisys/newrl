from utils import save_file_and_get_path
from codes.transactionmanager import Transactionmanager
from codes.addwallet import add_wallet
from fastapi.datastructures import UploadFile
from fastapi.params import File
import uvicorn
from fastapi import FastAPI

from codes import validator
from codes import signmanager
from codes import validator

app = FastAPI()


@app.post("/validate")
async def validate(transactionfile: UploadFile = File(...)):
    transactionfile_path = save_file_and_get_path(transactionfile)
    response = validator.validate(transactionfile_path)
    return {"status": "SUCCESS", "response": response}
    
@app.post("/add-wallet")
async def validate(custodian_address: str = "0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42",
    kyc1: UploadFile = File(...), kyc2: UploadFile = File(...)):
    f1 = save_file_and_get_path(kyc1)
    f2 = save_file_and_get_path(kyc2)
    newaddress = add_wallet(f1, f2, custodian_address)
    return {
        "status": "SUCCESS",
        "new_address": newaddress
    }

@app.post("/sign")
async def sign(custodian_address: str = "0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42", transactionfile: UploadFile = File(...)):
    transactionfile_path = save_file_and_get_path(transactionfile)
    sign_status = signmanager.sign(custodian_address, transactionfile_path)
    return {
        "status": "SUCCESS",
        "data": sign_status
    }

@app.post("/create-token")
async def create_token():
    return {"status": "SUCCESS"}

@app.post("/run-updater")
async def run_updater():
    return {"status": "SUCCESS"}


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8080)


from codes.addwallet import add_wallet
from fastapi.datastructures import UploadFile
from fastapi.params import File
import uvicorn
from fastapi import FastAPI

from codes import validator

app = FastAPI()


@app.post("/validate")
async def validate():
    try:
        response = validator.main()
        return {"status": "SUCCESS", "response": response}
    except Exception as e:
        return {"status": "ERROR", "response": str(e)}    

@app.post("/add-wallet")
async def validate(custodian_address: str = "0x7e433fd1cc776d17d4ad94daa2e1fc52ef967b42",
     kyc1: UploadFile = File(...),
                    kyc2: UploadFile = File(...)):
    
    print(kyc1.file, kyc2.file.name)
    file_location = f"/tmp/{kyc1.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(kyc1.file.read())
    f1 = file_location
    f2 = file_location
    newaddress = add_wallet(f1, f2, custodian_address)
    return {
        "status": "SUCCESS",
        "new_address": newaddress
    }

@app.post("/sign-transaction")
async def validate():
    return {"status": "SUCCESS"}

@app.post("/create-token")
async def validate():
    return {"status": "SUCCESS"}

@app.post("/run-updater")
async def validate():
    return {"status": "SUCCESS"}


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=9500)


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
async def validate():
    return {"status": "SUCCESS"}

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


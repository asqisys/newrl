import json
from sqlite3 import Cursor
from app.codes import nstablecoin

def test_usd1():
    callparams = {
        "address":None,
        "creator":"addressofcreator",
        "ts_init":None,
        "name":"nusd1",
        "version":"1.0.0",
        "actmode":"call",
        "status":0,
        "next_act_ts":None,
        "signatories":"",
        "parent":None,
        "oracleids":None,
        "selfdestruct":1,
        "contractspecs":{
                },
            "legalparams":{}
        }
    callparamjson=json.dumps(callparams)
    scoin1=nstablecoin.nusd1()
    cur = "x"
    scoin1.setup(cur, callparamjson)
    scoin1.deploy(cur, "sender", callparams={"trans_code":"123sdwe2"})
#    loan1=secloanv100.SecLoan1("0xa87cfed9b43a84d621b6ab4e2b928ac9c7e6c5df")

if __name__ == '__main__':
    test_secloan1()
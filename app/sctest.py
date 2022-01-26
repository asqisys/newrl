import json
import codes.nusd1 as ns
import importlib
import sqlite3

NEWRL_DB = "data/temp.db"

def test_usd1(cur):
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
            "legalparams":{"legaldochash":"mewmew"}
        }
    callparamjson=json.dumps(callparams)
    scoin1= ns.nusd1()
    scoin1.setup(cur, callparamjson)
    scoin1.deploy(cur, "sender", callparams={"trans_code":"123sdwe2"})
#    loan1=secloanv100.SecLoan1("0xa87cfed9b43a84d621b6ab4e2b928ac9c7e6c5df")

if __name__ == '__main__':
    string5 = '.'
    string4 = "randomtest"
    string2 = "TestClass"
    string3 = "change_funct"
#    module = importlib.import_module(string5, package=string4)
#    clas = getattr(module,string2)
#    testclass = clas()
#    funct = getattr(testclass, string3)
#    funct()
    con = sqlite3.connect(NEWRL_DB)
    cur = con.cursor()
    test_usd1(cur)
    con.commit()
    con.close()
    


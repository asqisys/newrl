import json
from codes import secloanv100
def test_secloan1():
    callparams = {
        "address":None,
        "creator":"addressofcreator",
        "ts_init":None,
        "name":"secloan1",
        "version":"1.0.0",
        "actmode":"hybrid",
        "status":0,
        "next_act_ts":None,
        "signatories":"",
        "parent":None,
        "oracleids":None,
        "selfdestruct":1,
        "contractspecs":{
                "tokencode":0,
                "loanamount":0,
                "repayment":0,
                "due_date":None,
                "ltv":0,
                "sec_token_code":0,
                "sec_token_amount":0,
                "borrowerwallet":"abcdef",
                "lenderwallet":"324543",
                "secprovider":None,
                "special_params":{}
                },
            "legalparams":{}
        }
    callparamjson=json.dumps(callparams)
#    loan1=secloanv100.SecLoan1()
#    loan1.setup(callparamjson)
#    loan1.create_loan_token()
    loan1=secloanv100.SecLoan1("0xa87cfed9b43a84d621b6ab4e2b928ac9c7e6c5df")
    loan1.create_loan_token()
if __name__ == '__main__':
    test_secloan1()
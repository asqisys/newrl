import json
from codes import secloanv100
def test_secloan1():
    callparams = {
        "address":None,
        "creator":"0x97246f464c273c8d223fd4c49d7a383713dbf798",
        "ts_init":None,
        "name":"secloan1",
        "version":"1.0.0",
        "actmode":"hybrid",
        "status":0,
        "next_act_ts":None,
        "signatories":["0x97246f464c273c8d223fd4c49d7a383713dbf798","0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848"],
        "parent":None,
        "oracleids":None,
        "selfdestruct":1,
        "contractspecs":{
                "tokencode":2,
                "loanamount":205,
                "repayment":210,
                "due_date":"2022-01-05",
                "ltv":70,
                "sec_token_code":4,
                "sec_token_amount":3,
                "borrowerwallet":"0x97246f464c273c8d223fd4c49d7a383713dbf798",
                "lenderwallet":"0xef1ab9086fcfcadfb52c203b44c355e4bcb0b848",
                "secprovider":"0x97246f464c273c8d223fd4c49d7a383713dbf798",
                "special_params":{}
                },
            "legalparams":{}
        }
    callparamjson=json.dumps(callparams)
#    loan1=secloanv100.SecLoan1()
#    loan1.setup(callparamjson)
#    loan1.create_loan_token()
    loan1=secloanv100.SecLoan1("0xaf5c0ef8e528a169fcfbdc47d6eec8e8ec083089")
    loantokentx, lendtransfertx, sectransfertx = loan1.create_child_txs()
    print(json.dumps(loantokentx))
    print(lendtransfertx)
    print(sectransfertx)
if __name__ == '__main__':
    test_secloan1()
import json
from codes import secloanv100
def test_secloan1():
    callparams = {"contractparams": 
    {
        "creator":"addressofcreator",
        "name":"secloan1",
        "version":"1.0.0",
        "actmode":"hybrid",
        "status":0,
        "next_act_ts":"",
        "signatories":"",
        "parentcontractaddress":None,
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
                "borrowerwallet":None,
                "lenderwallet":None,
                "secprovider":None,
                "special_params":{}
                },
            "legalparams":{}
        }
    }
    callparamjson=json.dumps(callparams)
#    loan1=secloanv100.SecLoan1()
#    loan1.setup(callparamjson)
#    loan1.create_loan_token()
    loan1=secloanv100.SecLoan1("0x6c08e77f695e38394fb8dd1a58f42b7394dac9a7")
if __name__ == '__main__':
    test_secloan1()
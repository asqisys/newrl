# Python programm to create object that enables addition of a block

import datetime
import sqlite3

from .transactionmanager import Transactionmanager

def create_token_transaction(token_data):
    con = sqlite3.connect('newrl.db')
    cur = con.cursor()
    token_cursor = cur.execute("SELECT tokencode FROM tokens where tokencode=?", (token_data["tokencode"],))
    row = token_cursor.fetchone()
    if row is not None:
        raise Exception('Token already exist with same code')
    
    # TODO - Token code need to be decided at the time of mining to avoid 
    #   duplicate codes from two tokens in mempool or from different nodes
    token_cursor = cur.execute("SELECT max(tokencode) FROM tokens").fetchone()
    maxtokencode = token_cursor[0] if token_cursor is not None else 0
    token_data["tokencode"] = maxtokencode + 1
    transaction = {
        'timestamp': str(datetime.datetime.now()),
        'type': 2,
        'currency': "INR",
        'fee': 0.0,
        'descr': "New token creation",
        'valid': 1,
        'block_index': 0,
        'specific_data': token_data
    }

    trans = Transactionmanager()
    transaction_data = {'transaction': transaction, 'signatures': []}
    trans.transactioncreator(transaction_data)
    transaction_file = trans.dumptransaction()
    return transaction_file


# class Tokenmanager():
#     def __init__(self, token_data=None):
#         self.tokenrecordsfile = "all_tokens.json"
#         self.tokendata = token_data
 
#     # def load_attributes(self,attfile):
#     # # this is expected to be useful in case one wants to specify token attributes in a separate file from token data
#     # 	with open(tokenfile,"r") as readfile:
#     # 		attributes=json.load(readfile);
#     # 		try:
#     # 			self.tokendata['tokenattributes']=attributes;
#     # 			return True
#     # 		except:
#     # 			print("Invalid file format")
#     # 			return False

#     def dumptokendata(self):
#         return self.tokendata
#         # this just dumps token data without checking about its validity or being present in records
#         with open(tokenfile, "w") as writefile:
#             try:
#                 json.dump(self.tokendata, writefile)
#             except:
#                 print("Couldn't dump data, probably wrong format")

#     def loadtoken(self, tokenfile):
#         # this function just loads a token from a file; may be valid or invalid, maybe in the records or not.
#         with open(tokenfile, "r") as readfile:
#             print("Now reading from ", tokenfile)
#             tokendata = json.load(readfile)
#             try:
#                 self.tokendata = tokendata
#             #	return True
#             except:
#                 print("Invalid file format")
#                 return False

#     def loadandcreate(self, token_data):
#         # this function loads presumably new token attributes from a file, with an intent to create a new token
#         # it ignore token code if any, increments it by 1 from tokenreocrds file and re-writes the tokenfile as well
#         # self.loadtoken(tokenfile)
#         self.tokendata = token_data
#         if self.istokeninrecords():
#             print("Either token already in record or token code reused. Set tokencode in file to 0 and try again if trying to add a new token. Else ignore")
#             return False
#         else:
#             maxtcode = self.maxtokencode()
#             self.tokendata["tokencode"] = maxtcode+1
#             # self.create_token()
#             # with open(tokenfile, "w") as writefile:
#             #     # writing back with updated tokencode to the tokefile
#             #     json.dump(self.tokendata, writefile)
#             # # now adidng transaction
#             transaction = {'timestamp': str(datetime.datetime.now()),
#                            #	'trans_code':"000000"
#                            'type': 2,
#                            'currency': "INR",
#                            'fee': 0.0,
#                            'descr': "New token creation",
#                            'valid': 1,
#                            'block_index': 0,
#                            'specific_data': self.tokendata}
#             trans = Transactionmanager()
#             signatures = []
#             transactiondata = {'transaction': transaction,
#                                'signatures': signatures}
#             trans.transactioncreator(transactiondata)
#             transaction_file = trans.dumptransaction()
#             return transaction_file

#     def istokeninrecords(self):
#         con = sqlite3.connect('newrl.db')
#         cur = con.cursor()
#         token_cursor = cur.execute("SELECT tokencode FROM tokens where tokencode=?", (self.tokendata["tokencode"],))
#         row = token_cursor.fetchone()
#         return row is not None


#     def maxtokencode(self):
#         con = sqlite3.connect('newrl.db')
#         cur = con.cursor()
#         token_cursor = cur.execute("SELECT max(tokencode) FROM tokens").fetchone()
#         maxtokencode = token_cursor[0] if token_cursor is not None else 0
#         return maxtokencode

#     def create_token(self):
#         # do not use this for creating a new token; this only adds new token to records; use loadandcreate instead
#         tokenrecordsfile = self.tokenrecordsfile
#         with open(tokenrecordsfile, "r+") as tokenrecords:
#             tokenrecs = json.load(tokenrecords)
#             newrecord = self.tokendata
# #			for tokenrec in tokenrecs
#             print("Adding new token in ", tokenrecordsfile)
#             try:
#                 tokenrecs.append(newrecord)
#                 tokenrecords.seek(0)
#                 json.dump(tokenrecs, tokenrecords)
#                 print("Successfully added new token to ", tokenrecordsfile)
#                 return True
#             except:
#                 print("Couldn't add new token.")
#                 return False


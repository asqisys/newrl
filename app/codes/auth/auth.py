
import json

from app.constants import AUTH_FILE_PATH
from ..crypto import sign_object


def get_wallet():
    try:
        with open(AUTH_FILE_PATH, 'r') as f:
            auth_data = json.load(f)
            wallet = auth_data['wallet']
            return wallet
    except:
        return {}


def get_auth():
    try:
        with open(AUTH_FILE_PATH, 'r') as f:
            auth_data = json.load(f)
            wallet = auth_data['wallet']
            private_key = wallet['privateKey']
            auth_data = {
                'person_id': auth_data['person_id'],
                'wallet_id': wallet['address'],
                'publicKey': wallet['publicKey'],
            }
            auth_data['signature'] = sign_object(private_key, auth_data)
            print('auth', auth_data)
            return auth_data
    except:
        auth_data = {}
        print(f'Could not get auth data. Make auth file {AUTH_FILE_PATH} is present')

try:
    auth_data = get_auth()
except:
    auth_data = {}
    print(f'Could not get auth data. Make auth file {AUTH_FILE_PATH} is present')
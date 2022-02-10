import requests
from app.codes.p2p.sync_mempool import receive_transaction
from app.constants import TRANSPORT_SERVER
from app.codes.p2p.sync_chain import receive_block, receive_receipt


def receive(payload):
    try:
        operation = payload['operation']
        data = payload['data']

        if operation == 'send_transaction':
            print('Received transaction', data)
            receive_transaction(data)
        elif operation == 'send_block':
            print('Received block', data)
            receive_block(data)
        elif operation == 'send_receipt':
            print('Received block', data)
            receive_receipt(data)
        else:
            print('Unknown operation', operation)
    except Exception as e:
        print(e)
        return 'Invalid payload'

def send_to_peers(operation, data):
    payload = {
        'operation': operation,
        'data': data
    }
    try:
        send(payload)
    except:
        print('Error sending transaction to transport server')


def send(payload):
    response = requests.post(TRANSPORT_SERVER + '/send', json=payload)
    if response.status_code != 200:
        print('Error sending')
    return response.text

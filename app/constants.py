"""Global constants in this file"""
import os

IS_TEST = os.environ.get('NEWRL_TEST') is not None
if IS_TEST:
    print('Using constants for Test')

DATA_PATH = 'data_test/' if IS_TEST else 'data/'
MEMPOOL_PATH = DATA_PATH + 'mempool/'
TMP_PATH = DATA_PATH + 'tmp/'
INCOMING_PATH = DATA_PATH + 'tmp/incoming/'
NEWRL_DB = DATA_PATH + 'newrl.db'
NEWRL_P2P_DB = DATA_PATH + 'newrl_p2p.db'
STATE_FILE = 'state.json'
CHAIN_FILE = 'chain.json'
ALLOWED_CUSTODIANS_FILE = 'allowed_custodians.json'
DB_MIGRATIONS_PATH = 'app/migrations/migrations'
AUTH_FILE_PATH = '.auth.json'

BOOTSTRAP_NODES = ['newrl.net']
REQUEST_TIMEOUT = 5
NEWRL_PORT = 8090
NEWRL_TOKEN = "newrl_token"
TREASURY = "treasury_address"
COINBASE_SC = "coinbase_sc_address"
TRANSPORT_SERVER = 'http://localhost:8095'

COMMITTEE_SIZE = 6
MINIMUM_ACCEPTANCE_VOTES = 4
MINIMUM_ACCEPTANCE_RATIO = 0.6
NO_RECEIPT_COMMITTEE_TIMEOUT = 10  # Timeout in seconds
NO_BLOCK_TIMEOUT = 5  # No block received timeout in seconds

# Variables
TIME_DIFF_WITH_GLOBAL = 0
MAX_ALLOWED_TIME_DIFF_SECONDS = 10
BLOCK_TIME_INTERVAL_SECONDS = 30
MY_ADDRESS = ''

import os
from ..constants import INCOMING_PATH, MEMPOOL_PATH, TMP_PATH, DATA_PATH
from ..migrations.init_db import init_db, init_trust_db


def init_newrl():
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    if not os.path.exists(MEMPOOL_PATH):
        os.mkdir(MEMPOOL_PATH)
    if not os.path.exists(TMP_PATH):
        os.mkdir(TMP_PATH)
    if not os.path.exists(INCOMING_PATH):
        os.mkdir(INCOMING_PATH)

    # clear_db()
    init_db()
    init_trust_db()

    # TODO - Run migrations

if __name__ == '__main__':
    init_newrl()
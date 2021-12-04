# Python programm to create the genesis block with a given chain creator wallet address

import json
import os
import shutil

from .blockchain import Blockchain
from .constants import ALL_WALLETS_FILE, CHAIN_FILE, MEMPOOL_PATH


def main():
    blockchain = Blockchain(CHAIN_FILE)
    print("Loaded chain validity status : ",
          blockchain.chain_valid(blockchain.chain))

    empty = []
    with open("empty.json", "w") as writefile:
        json.dump(empty, writefile)

    if not os.path.exists(ALL_WALLETS_FILE):
        #	shutil.copy("creatorwalletdata.json","all_wallets.json")
        print("all_wallets.json does not exist, creating. Signing won't work till valid addresses added to it.")
        allw = []
        with open(ALL_WALLETS_FILE, "w") as writefile:
            json.dump(allw, writefile)
    else:
        print("all_wallets.json already exists. Signing will work for addresses in it.")

    if not os.path.exists("all_tokens.json"):
        shutil.copy("empty.json", "all_tokens.json")
    else:
        print("all_tokens.json already exists.")

    print("Making mempool, incltranspool and statearchive directories")
    if not os.path.exists(MEMPOOL_PATH):
        os.mkdir(MEMPOOL_PATH)
    else:
        print("WRN: Mempool already exists, beware of possible errors")
    # if not os.path.exists("./incltranspool/"):
    # 	os.mkdir("./incltranspool/")
    # else:
    # 	print("WRN: Incltranspool already exists, beware of possible errors")
    # if not os.path.exists("./statearchive/"):
    # 	os.mkdir("./statearchive/")
    # else:
    # 	print("WRN: statearchive  already exists, beware of possible errors")


if __name__ == "__main__":
    main()

import json
from codes import updater

def test_update_db_states():
    with open('chain.json', 'r') as file:
        chain = json.load(file)
        for block in chain:
            print(block['text']['transactions'])
            updater.update_db_states(block['text']['transactions'])


if __name__ == '__main__':
    test_update_db_states()
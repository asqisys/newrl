import importlib


def run(contract_name, args):
    CONTRACTS_PATH = 'contracts.'
    contract = importlib.import_module(CONTRACTS_PATH + contract_name)
    return contract.run(args)


def setup(contract_name, args):
    CONTRACTS_PATH = 'contracts.'
    contract = importlib.import_module(CONTRACTS_PATH + contract_name)
    return contract.setup(args)

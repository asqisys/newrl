def setup(args):
    pass

def run(args):
    print('Running contract with args', args)
    return {'status': 'SUCCESS', 'detail': 'Ran simple loan v1 with args ' + str(args)}
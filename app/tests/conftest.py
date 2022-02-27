import os
import shutil
import pytest

from ..codes.p2p.peers import init_peer_db

def setup_test_files():
    """Setup test files"""
    print('Setting up test files')
    if not os.path.exists('data_test/'):
        os.makedirs('data_test/')
    if os.path.exists('data_test/newrl.db'):
        os.remove('data_test/newrl.db')
    if os.path.exists('data_test/newrl_p2p.db'):
        os.remove('data_test/newrl_p2p.db')
    shutil.copyfile('data_test/template/newrl.db', 'data_test/newrl.db')
    init_peer_db()


@pytest.fixture(scope="session", autouse=True)
def my_setup(request):
    setup_test_files()
    def fin():
        print ("Doing teardown")
    request.addfinalizer(fin)
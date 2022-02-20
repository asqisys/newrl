import os
import shutil
import pytest


def setup_test_files():
    """Setup test files"""
    print('Setting up test files')
    if not os.path.exists('data_test/'):
        os.makedirs('data_test/')
    if not os.path.exists('data_test/newrl.db'):
        os.remove('data_test/newrl.db')
    shutil.copyfile('data_test/template/newrl.db', 'data_test/newrl.db')


@pytest.fixture(scope="session", autouse=True)
def my_setup(request):
    setup_test_files()
    def fin():
        print ("Doing teardown")
    request.addfinalizer(fin)
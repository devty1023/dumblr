import os
import pickle
import pytest
from dumblr.core import Dumblr

@pytest.fixture()
def nodumblr(tmpdir, request):
    # change cwd to tmpdir
    cwd = os.getcwd()
    os.chdir(tmpdir.strpath)

    def fin():
        # revert back to original dir
        print cwd
        os.chdir(cwd)

    request.addfinalizer(fin)
    return Dumblr()

@pytest.fixture()
def dumblr(tmpdir, request):
    p = tmpdir.mkdir(".dumblr").join("DUMBLR")

    # test DUMBLR config file
    with open(p.strpath, "w") as f:
        dat = {'config': {'consumer_key' : 'foo'},
               'tumblr': 'bar'}
        pickle.dump(dat, f)

    # change cwd to tmpdir
    cwd = os.getcwd()
    os.chdir(tmpdir.strpath)

    def fin():
        # revert back to original dir
        print cwd
        os.chdir(cwd)

    request.addfinalizer(fin)

    return Dumblr()

def test_dumblr_noinit(nodumblr):
    assert nodumblr.initialized == False

def test_dumblr_init(dumblr):
    assert dumblr.initialized == True
    assert "DUMBLR" in dumblr.DATA_FILE
    assert ".dumblr" in dumblr.dumblr_path
    data = {'config': {'consumer_key' : 'foo'}, 'tumblr': 'bar'}
    assert dumblr.DATA == data
    
def test_dumblr_initialize(dumblr):
    # TODO : blocked b/c of Tumblr.oauth() method
    assert True

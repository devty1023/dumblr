import pytest
from dumblr.utils import get_dumblr_root, assert_dumblr_root

def test_get_dumblr_root_no(tmpdir):
    assert get_dumblr_root(tmpdir.strpath) == ""

def test_get_dumblr_root_yes(tmpdir):
    tmpdir.mkdir(".dumblr")
    assert get_dumblr_root(tmpdir.strpath) == tmpdir.strpath

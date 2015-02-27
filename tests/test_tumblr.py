import json
import pytest
from dumblr.tumblr import Tumblr

@pytest.fixture
def tokens():
    with open("tests/tumblr_credentials.json") as f:
        return json.loads(f.read())

@pytest.fixture
def tumblr(tokens):
    return Tumblr(tokens['consumer_key'],
                  tokens['secret_key'],
                  tokens['oauth_token'],
                  tokens['oauth_token_secret'])

def test_oauth():
    ## TODO
    assert True

def test_tumblr_info(tumblr):
    i = tumblr.info()
    props = {'name' : "devty1023"}
    assert all([i[prop] == props[prop] for prop in props.keys()])

def test_tumblr_posts(tumblr):
    i = tumblr.get_text_posts('devty1023')
    assert len(i) > 0
    props = ['body', 'date', 'format', 'slug', 'title', 'tags', 'state', 'id']
    assert all([prop in i[0] for prop in props])

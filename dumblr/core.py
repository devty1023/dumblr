import click
import cPickle
import os
import shutil
import tumblr
from utils import get_dumblr_root

class Dumblr(object):
    def __init__(self):
        self.initialized = True
        root_path = get_dumblr_root(os.getcwd())

        if not root_path:
            self.initialized = False
            root_path = os.getcwd()

        self.root_path = root_path
        self.dumblr_path = os.path.join(root_path, ".dumblr")
        self.DATA_FILE = os.path.join(self.dumblr_path, "DUMBLR")
        self.DATA = self.load_data()

    def load_data(self):
        """Unpickles data file stored in DATA_FILE.
        If DATA_FILE does not exists, returns only basic info
        """
        dat = {}

        if os.path.isfile(self.DATA_FILE):
            with open(self.DATA_FILE) as f:
                loaded = cPickle.load(f)
                dat.update(loaded)

        return dat

    def initialize(self):
        """Completes the following tasks.
        
        1. Obtain Tumblr OAuth
        2. Get basic user info from Tumblr
        3. Create directory .dumblr 
        - if directory already exists, we remove it
        4. Pickles configuration data into .dumblr/DUMBLR
        """
        d = {}
        d['config'] = tumblr.Tumblr.oauth()

        t = tumblr.Tumblr(d['config']['consumer_key'],
                          d['config']['secret_key'],
                          d['config']['oauth_token'],
                          d['config']['oauth_token_secret'])
        ## IMPORTANT: We only consider blog named after username
        ## Later update `might` address this issue
        d['tumblr'] = t.info()

        if os.path.isdir(self.dumblr_path):
            shutil.rmtree(self.dumblr_path)

        os.makedirs(self.dumblr_path)

        with open(self.DATA_FILE, "w") as f:
            cPickle.dump(d, f)

        click.secho("Initialized dumblr at {}".format(self.dumblr_path))

    def pull(self, load=True):
        """Pulls all text posts from Tumblr.

        Retrieved text posts is stored in .dumblr/TUMBLR,
        later to be used to compare with commited data.

        If load is set to true, post data will be converted and
        loaded onto the file system on root_path/posts
        """
        ## get all published and draft text posts from tumblr
        config = self.DATA['config']
        t_config = self.DATA['tumblr']
        t = tumblr.Tumblr(config['consumer_key'],
                          config['secret_key'],
                          config['oauth_token'],
                          config['oauth_token_secret'])
        posts = t.get_text_posts(t_config['name'])

        click.echo(posts)
        return posts

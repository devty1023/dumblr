import click
import cPickle
import datetime
import difflib
import json
import os
import yaml
import re
import shutil
import tumblr
from codecs import open
from textwrap import dedent, wrap
from unidecode import unidecode
from utils import get_dumblr_root

class Dumblr(object):
    def __init__(self):
        self.initialized = True
        root_path = get_dumblr_root(os.getcwd())

        if not root_path:
            self.initialized = False
            root_path = os.getcwd()

        self.root_path = root_path
        self.posts_path = os.path.join(root_path, "posts")
        self.dumblr_path = os.path.join(root_path, ".dumblr")
        # config file contains meta info to run dumblr
        self.CONFIG_FILE = os.path.join(self.dumblr_path, "DUMBLR")
        # tumblr file contains text posts in tumblr as observed at the time
        self.TUMBLR_FILE = os.path.join(self.dumblr_path, "TUMBLR")

        self.CONFIG = self.load_data()


    def load_data(self):
        """Unpickles data file stored in self.CONFIG_FILE
        If the file does not exists, returns default info (nothing).
        """
        dat = {}
        if os.path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE) as f:
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

        with open(self.CONFIG_FILE, 'w') as f:
            cPickle.dump(d, f)

        return self.dumblr_path

    def pull(self):
        """Pulls all text posts from Tumblr.

        Retrieved text posts is stored in .dumblr/TUMBLR,
        later to be used to compare with commited data.

        If load is set to true, post data will be converted and
        dumped to the file system on self.posts_path.
        """
        ## get all published and draft text posts from tumblr
        t_config = self.CONFIG['tumblr']
        t = self._get_tumblr()
        posts = t.get_text_posts(t_config['name'])

        ## save posts to TUMBLR_FILE
        with open(self.TUMBLR_FILE, 'w') as f:
            cPickle.dump(posts, f)

        return posts, t_config['name']

    def new(self, postname, _format):
        slug = Dumblr.slugify(postname)
        fpath = os.path.join(self.posts_path, 
                             "{}.{}".format(slug, _format))

        fm = {'title' : postname,
              'date' : "{} GMT".format(datetime.datetime.utcnow()),
              'slug' : slug,
              'tags' : [],
              'format' : _format,
              'state' : "draft",
              'id': -1}
        frontmatter = self._dump_frontmatter(fm)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)

        return fpath
        
    def load(self):
        """Loads posts to the file system.
        
        Each post will be a editable text file with 
        extension {.html|.md} depending on the format described.

        The posts will live in the directory self.posts_path.
        If a file already exists with the target post file name,
        it will be OVERWRITTEN!
        """
        if not os.path.isdir(self.posts_path):
            os.makedirs(self.posts_path)
            
        posts = {}

        with open(self.TUMBLR_FILE) as f:
            posts = cPickle.load(f)

        for post in posts:
            filename = "{}.{}".format(post['slug'], post['format'])
            filepath = os.path.join(self.posts_path, filename)
            frontmatter = self._dump_frontmatter(post)

            with open(filepath, "w", encoding='utf-8') as f:
                body = frontmatter + post['body']
                f.write(body)

        return ["{}.{}".format(post['slug'], post['format'])
                for post in posts]

    def dump(self):
        """Dumps posts from the file system

        Each valid text post in self.posts_path is
        parsed to generate a list of posts.
        """
        posts_f = []
        if os.path.exists(self.posts_path):
            posts_f = [os.path.join(self.posts_path, f) 
                       for f in os.listdir(self.posts_path) 
                       if os.path.isfile(os.path.join(self.posts_path,f))]
        
        posts = map(Dumblr.parse_frontmatter, posts_f)
        posts = [post for post in posts if post] # remove None
        return posts

    def status(self):
        """Reports difference between posts in the fs
        and the posts saved in TUMBLR file
        """
        fs_posts = self.dump()
        tb_posts = []

        with open(self.TUMBLR_FILE) as f:
            try:
                tb_posts = cPickle.load(f)
            except:
                ## user never pulled from tumblr
                pass
            
        posts = []
        for fs_p in fs_posts:
            ## find corresponding posts on TUMBLR
            tb_p = next((p for p in tb_posts
                         if p['id'] == fs_p['id']), None)
            if tb_p:
                diff = Dumblr.diff_post(tb_p, fs_p)
                if diff:
                    posts.append({'action' : 'update',
                                  'post' : fs_p,
                                  'diff' : diff})
            else:
                posts.append({'action' : 'create',
                              'post' : fs_p})

        for tb_p in tb_posts:
            fs_p = next((p for p in fs_posts
                         if p['id'] == tb_p['id']), None)
            if not fs_p:
                posts.append({'action' : 'delete',
                              'post' : tb_p})
            
        return posts

    def diff(self):
        """Reports specific difference for a given list
        of posts

        Returns a dictionary that maps postname 
        to its diff report
        """
        posts = self.status()
        updates = filter(lambda x : x['action'] == 'update', posts)

        d = difflib.Differ()
        diff_result = {}
        for update in updates:
            post = update['post']
            diffs = update['diff']

            diff_attr = {}
            for k, diff in diffs.iteritems():
                print diff
                diff_str = list(d.compare(wrap(str(diff[0]), 60),
                                          wrap(str(diff[1]), 60)))
                diff_attr[k] = "\n\t".join(diff_str)

            postname = "{}.{}".format(post['slug'], post['format'])
            diff_result[postname]= diff_attr

        return diff_result

    def push(self):
        """Pushes changes in the posts in the filesystem
        directly to dumblr
        """
        t_config = self.CONFIG['tumblr']
        t = self._get_tumblr()
    
    def _get_tumblr(self):
        config = self.CONFIG['config']
        return tumblr.Tumblr(config['consumer_key'],
                             config['secret_key'],
                             config['oauth_token'],
                             config['oauth_token_secret'])

    def _dump_frontmatter(self, post):
        ## python's list of string prints
        ## strings within single quotes
        ## this doesn't work well with
        ## python's yaml library
        post['tags'] = u"[{0}]".format(u", ".join([tag for tag in post['tags']]))
        frontmatter = dedent(u"""\
        ---
        title: {title}
        date: {date}
        slug: {slug}
        tags: {tags}
        format: {format}
        state: {state}
        id: {id}
        ---
        """.format(**post))
        return frontmatter
            
        
    @staticmethod
    def diff_post(p1, p2):
        """Diffs two of posts and returns
        a map containing different attributes.
        
        e.g.
        diff({'title': 'foo', 'body': 'bar', 'id' : 1},
        {'title': 'Foo', 'body': 'Bar', 'id' : 1})
        => {'title' : ['foo', 'Foo'],
        'body' : ['bar', 'Bar']}
        """
        return {k : [p1_v, p2[k]] for k, p1_v in p1.iteritems()
                if p2[k] != p1_v}

    @staticmethod
    def slugify(text, delim=u'-'):
        """by Armin Ronacher

        http://flask.pocoo.org/snippets/5/
        """
        _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
        result = []
        for word in _punct_re.split(text.lower()):
            result.extend(unidecode(word).split())
        return unicode(delim.join(result))

    @staticmethod
    def parse_frontmatter(filename):
        reg_fm = re.compile(r'^-{3,}$', re.MULTILINE)
        try:
            with open(filename, encoding='utf-8') as f:
                _, fm, content = reg_fm.split(f.read(), 2)
                p = yaml.load(fm)
                p.update({'body' : content.lstrip()})
                return p
        except (ValueError, IOError) as e:
            return None



        

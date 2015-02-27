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

        with open(self.CONFIG_FILE, "w") as f:
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
        config = self.CONFIG['config']
        t_config = self.CONFIG['tumblr']
        t = tumblr.Tumblr(config['consumer_key'],
                          config['secret_key'],
                          config['oauth_token'],
                          config['oauth_token_secret'])
        posts = t.get_text_posts(t_config['name'])

        ## save posts to TUMBLR_FILE
        with open(self.TUMBLR_FILE, "w") as f:
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
              'state' : "new",
              'id': -1}

        frontmatter = dedent("""\
        ---
        title: {title}
        date: {date}
        slug: {slug}
        tags: {tags}
        format: {format}
        state: {state}
        id: {id}
        ---
        """.format(**fm))

        with open(fpath, 'w') as f:
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

            frontmatter = dedent("""\
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

            with open(filepath, "w") as f:
                f.write(frontmatter + post['body'])

        return ["{}.{}".format(post['slug'], post['format'])
                for post in posts]

    def dump(self):
        """Dumps posts from the file system

        Each valid text post in self.posts_path is
        parsed to generate a list of posts.
        """
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

        ## we potentially have 2 tasks
        ## creating a post OR updating a post
        create = []
        update = []
        for fs_p in fs_posts:
            ## find corresponding posts on tumblr
            tb_p = next((p for p in tb_posts
                         if p['id'] == fs_p['id']), None)
            if tb_p:
                diff = Dumblr.diff_post(tb_p, fs_p)
                if diff:
                    update.append({'goal' : fs_p, 'diff' : diff})
            else:
                create.append(fs_p)

        return create, update

    def diff(self):
        """Reports specific difference for a given list
        of posts

        Returns a dictionary that maps postname 
        to its diff report
        """
        _, updated = self.status()

        diff_result = {}
        d = difflib.Differ()
        for candidate in updated:
            post = candidate['goal']
            diffs = candidate['diff']

            diff_attr = {}
            for k, diff in diffs.iteritems():
                diff_str = list(d.compare(wrap(diff[0], 60), wrap(diff[1], 60)))
                diff_attr[k] = "\n\t".join(diff_str)

            postname = "{}.{}".format(post['slug'], post['format'])
            diff_result[postname]= diff_attr

        return diff_result
            
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
            with open(filename) as f:
                _, fm, content = reg_fm.split(f.read(), 2)
                p = yaml.load(fm)
                p.update({'body' : content.lstrip()})
                return p
        except (ValueError, IOError) as e:
            return None



        

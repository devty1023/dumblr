import os
import pickle
import pytest
from dumblr.core import Dumblr
from textwrap import dedent

@pytest.fixture()
def nodumblr(tmpdir, request):
    ## change cwd to tmpdir
    cwd = os.getcwd()
    os.chdir(tmpdir.strpath)

    def fin():
        ## revert back to original dir
        print cwd
        os.chdir(cwd)

    request.addfinalizer(fin)
    return Dumblr()

@pytest.fixture()
def dumblr(tmpdir, request):
    d = tmpdir.mkdir(".dumblr").join("DUMBLR")

    ## test DUMBLR config file
    dat = {'config': {'consumer_key' : 'foo'},
           'tumblr': 'bar'}
    d.dump(dat)

    ## test TUMBLR posts file
    ## TUMBLR will contain 3 files (ids 0 - 2)
    d = tmpdir.join(".dumblr").join("TUMBLR")
    posts = [{'body' : "hello world",
              'title' : "testpost-{}".format(i),
              'date' : "2015-02-19 02:14:57 GMT",
              'slug' : "testpost-{}".format(i),
              'tags' : [],
              'state' : "published",
              'id' : i,
              'format' : "markdown"} for i in range(3)]
    d.dump(posts)

    ## test dumblr posts in fs
    ## file system will contain 3 files (ids 1 - 3)
    d = tmpdir.mkdir("posts")
    for i in range(1, 4):
        fname = "testpost-{}".format(i) + ".markdown"
        post_meta = {'title' : "testpost-{}".format(i),
                     'date' : "2015-02-19 02:14:57 GMT",
                     'slug' : "testpost-{}".format(i),
                     'tags' : [],
                     'state' : "published",
                     'id' : i,
                     'format' : "markdown"}

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
        """.format(**post_meta))
        body = "hello world!"

        p = d.join(fname)
        p.write(frontmatter + body)

    ## change cwd to tmpdir
    cwd = os.getcwd()
    os.chdir(tmpdir.strpath)

    def fin():
        ## revert back to original dir
        print cwd
        os.chdir(cwd)

    request.addfinalizer(fin)

    return Dumblr()

def test_dumblr_noinit(nodumblr):
    assert nodumblr.initialized == False

def test_dumblr_init(dumblr):
    assert dumblr.initialized == True
    assert "DUMBLR" in dumblr.CONFIG_FILE
    assert "TUMBLR" in dumblr.TUMBLR_FILE
    assert ".dumblr" in dumblr.dumblr_path
    data = {'config': {'consumer_key' : 'foo'}, 'tumblr': 'bar'}
    assert dumblr.CONFIG == data
    
def test_dumblr_initialize(dumblr):
    ## TODO : blocked b/c of Tumblr.oauth() method
    assert True
    
def test_dumblr_load(dumblr, tmpdir):
    dumblr.load()

    ## overriding existing posts dir
    p = tmpdir.join("posts")
    assert p.ensure(dir=True)
    assert len(p.listdir()) == 4

    ## creating posts dir
    tmpdir.join("posts").remove()
    dumblr.load()  
    
    p = tmpdir.join("posts")
    assert p.ensure(dir=True)
    assert len(p.listdir()) == 3

    p0 = p.join("testpost-0.markdown")
    assert p0.ensure()

def test_dumblr_dump(dumblr, tmpdir):
    posts = [{'body' : "hello world!",
              'title' : "testpost-{}".format(i),
              'date' : "2015-02-19 02:14:57 GMT",
              'slug' : "testpost-{}".format(i),
              'tags' : [],
              'state' : "published",
              'id' : i,
              'format' : "markdown"} for i in range(1, 4)]
    l_posts = dumblr.dump()
    assert posts == l_posts

def test_dumblr_new(dumblr, tmpdir):
    dumblr.new("hello world!", "markdown")
    f = tmpdir.join("posts").join("hello-world.markdown")
    assert f.ensure()

    meta = {'title' : "hello world!",
            'slug' : "hello-world",
            'tags' : [],
            'state' : "draft",
            'id' : -1,
            'format' : "markdown"}
    f_meta = Dumblr.parse_frontmatter(f.strpath)
    assert all([f_meta[k] == v for k,v in meta.iteritems()])

def test_dumblr_status(dumblr):
    posts = dumblr.status()
    create = filter(lambda x : x['action'] == 'create', posts)
    update = filter(lambda x : x['action'] == 'update', posts)
    delete = filter(lambda x : x['action'] == 'delete', posts)
    assert len(create) == 1
    assert {'title' : "testpost-3",
            'date' : "2015-02-19 02:14:57 GMT",
            'slug' : "testpost-3",
            'tags' : [],
            'state' : "published",
            'id' : 3,
            'format' : "markdown",
            'body' : "hello world!"} == create[0]['post']
    assert 2 == len(update)
    assert len(delete) == 1

def test_dumblr_diff(dumblr):
    "TODO: a little hard to test this.."
    diffs = dumblr.diff()
    assert 2 == len(diffs)
    assert diffs.has_key('testpost-1.markdown')
    assert diffs.has_key('testpost-2.markdown')

def test_dumblr_static_diff_post():
    assert {'title' : ["foo", "Foo"],
            'body': ["bar", "Bar"]} == Dumblr.diff_post(
                {'title': 'foo', 'body': 'bar', 'id' : 1},
                {'title': 'Foo', 'body': 'Bar', 'id' : 1})

def test_dumblr_static_parse_frontmatter(dumblr, tmpdir):
    p = tmpdir.join("posts").join("testpost-1.markdown")
    fm = {'body' : "hello world!",
          'title' : "testpost-1",
          'date' : "2015-02-19 02:14:57 GMT",
          'slug' : "testpost-1",
          'tags' : [],
          'state' : "published",
          'id' : 1,
          'format' : "markdown"}
    assert fm == Dumblr.parse_frontmatter(p.strpath)

def test_dumblr_static_slugify():
    assert "hello-world" == Dumblr.slugify("hello world")

def test_dumblr_pull(dumblr, tmpdir):
    ## TODO: Create a test blog
    pass

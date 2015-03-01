import click
from core import Dumblr
from exceptions import DumblrException
from utils import get_dumblr_root, assert_dumblr_root

pass_dumblr = click.make_pass_decorator(Dumblr, ensure=True)

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('1.0')
    ctx.exit()

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@pass_dumblr
def cli(dumblr):
    pass

@cli.command()
@pass_dumblr
def init(d):
    """Initialize dumblr directory"""
    if d.initialized:
        ## dumblr directory already exists
        ## does user want to reinitalize?
        click.secho("Dumblr is already active")
        if not click.confirm('Do you want to reinitiazlied dumblr?'):
            return

    try:
        root = d.initialize()
    except DumblrException as e:
        click.secho("FATAL: {}".format(e))
        return
        
    click.secho("Initialized dumblr at {}".format(root))

@cli.command()
@pass_dumblr
@assert_dumblr_root
def pull(d):
    """Pulls posts from Tumblr"""
    try:
        posts, name = d.pull()
    except DumblrException as e:
        click.secho("FATAL: {}".format(e))
        return

    click.secho("# From blog {}\n#".format(name), bold=True)
    for post in posts:
        click.secho("#\tRetrieved : {}.{}".format(post['slug'], post['format']))
    click.secho("#\n# Total : {}".format(len(posts)), bold=True)

@cli.command()
@pass_dumblr
@assert_dumblr_root
def load(dumblr):
    """Loads posts pulled from tumblr to fs"""
    posts = dumblr.load()

    click.secho("# Loading to {}\n#".format(dumblr.posts_path), bold=True)
    for post in posts:
        click.secho("#\t{}".format(post))
    click.secho("#\n# Total : {}".format(len(posts)), bold=True)

@cli.command()
@click.argument('postname')
@click.option('--format', '-f',
                type=click.Choice(['html', 'markdown']),
                default='markdown') 
@pass_dumblr
@assert_dumblr_root
def new(dumblr, postname, format):
    """Create new post"""
    post = dumblr.new(postname, format)

    click.secho("# Created new post {}".format(post))

@cli.command()
@pass_dumblr
@assert_dumblr_root
def status(dumblr):
    """Checks status of posts in file system"""
    posts = dumblr.status()

    click.secho("# Status on directory {}\n#".format(dumblr.posts_path),
                bold=True)
    if posts:
        for post in posts:
            if post['action'] == 'create':
                echo_str =  "#\tnew post\t: {}.{}"
            elif post['action'] == 'update':
                echo_str = "#\tmodified\t: {}.{}"
            elif post['action'] == 'delete':
                echo_str = "#\t deleted\t: {}.{}"
            else:
                continue
            click.secho(echo_str.format(post['post']['slug'],
                                        post['post']['format']))
    else:
        click.secho("#\tNo change detected")
    click.secho("#")

@cli.command()
@pass_dumblr
@assert_dumblr_root
def diff(dumblr):
    """Generates diff report for updated posts
    """
    posts = dumblr.diff()
    
    click.secho("# Diff result:\n#", bold=True)
    if posts:
        for post, diffs in posts.iteritems():
            click.secho(post+"\n", bold=True)
            for attr, diff in diffs.iteritems():
                click.secho("\t"+attr, bold=True)
                click.secho("\t"+diff+"\n")
    else:
        click.secho("#\tNothing to do here")
    click.secho("#")

@cli.command()
@pass_dumblr
@assert_dumblr_root
def push(dumblr):
    """Pushes changes to Tumblr"""
    try:
        resps = dumblr.push()
    except DumblrException as e:
        click.secho("FATAL: {}".format(e))
        return

    click.secho("# Push result:\n#", bold=True)
    for resp in resps:
        click.secho("#\t{}\t: {}".format(resp['status'],
                                         resp['post']))
    click.secho("#")


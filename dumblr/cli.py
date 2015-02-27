import click
from core import Dumblr
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
    root = d.initialize()
    click.secho("Initialized dumblr at {}".format(root))

@cli.command()
@pass_dumblr
@assert_dumblr_root
def pull(d):
    """Pulls posts from Tumblr"""
    posts, name = d.pull()
    click.secho("# From blog {}\n#".format(name), bold=True)
    for post in posts:
        click.secho("#\tRetrieved : {}.{}".format(post['slug'], post['format']))
    click.secho("#\n# Total : {}".format(len(posts)), bold=True)

@cli.command()
@pass_dumblr
@assert_dumblr_root
def load(dumblr):
    """Loads posts pulled from tumblr to fs"""
    click.secho("# Loading to {}\n#".format(dumblr.posts_path), bold=True)

    posts = dumblr.load()
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
    click.secho("# Status on directory {}\n#".format(dumblr.posts_path),
                bold=True)

    create, update = dumblr.status()

    if create or update:
        if create:
            for post in create:
                click.secho("#\tnew post\t: {}.{}".format(post['slug'],
                                                          post['format']))
        if update:
            for i, post in enumerate(update):
                click.secho("#\tmodified\t: {}.{}".format(post['goal']['slug'],
                                                          post['goal']['format']))
    else:
        click.secho("#No change detected")
    click.secho("#")

@cli.command()
@pass_dumblr
@assert_dumblr_root
def diff(dumblr):
    """Generates diff report for updated posts
    """
    posts = dumblr.diff()
    
    click.secho("# Diff Result:\n#", bold=True)
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
@click.pass_context
def push(ctx):
    """Pushes commited changes to Tumblr"""
    pass


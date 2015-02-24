import click
import os
import shutil
from core import Dumblr
from utils import get_dumblr_root, assert_dumblr_root

pass_dumblr = click.make_pass_decorator(Dumblr, ensure=True)

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version 1.0')
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
    d.initialize()

@cli.command()
@click.argument('postname')
@assert_dumblr_root
def new(ctx, postname):
    """Create new post"""
    click.echo("Creating new post")
    pass

@cli.command()
@pass_dumblr
@assert_dumblr_root
def pull(d):
    """Pulls posts from Tumblr"""
    d.pull()
        

@cli.command()
@click.pass_context
def commit(ctx):
    """Commits changes made to posts in the file system"""
    pass

@cli.command()
@click.pass_context
def push(ctx):
    """Pushes commited changes to Tumblr"""
    pass

@cli.command()
@click.pass_context
def status(ctx):
    """Checks status of posts in file system"""
    pass
        

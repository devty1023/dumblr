import click
import os
import os.path as osp
import sys
from functools import wraps

def get_dumblr_root(path):
    """Returns path of dumblr repo, else 
    returns empty string
    
    Recursively checks travels up the directory
    to check the existence of ".dumblr" directory.
    
    Returns the directory that contains .dumblr
    subdirectory, empty string otherwise."""
    dumblr_dir = ".dumblr"
    path = osp.abspath(path)

    if osp.abspath("/") == path:
        return ""
    elif osp.exists(osp.join(path, dumblr_dir)):
        return path
    else:
        return get_dumblr_root(osp.join(path, ".."))

def assert_dumblr_root(f):
    @wraps(f)
    def g(*args, **kwargs):
        if not get_dumblr_root(os.getcwd()):
            click.echo("FATAL: Not a dubmlr repository!")
            click.echo("Try running `dumblr init`")
            sys.exit(1)
        return f(*args, **kwargs)
    return g

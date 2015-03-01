# dumblr

dumblr is an attempt to use tumblr like a blog backed by a static site generator.

## Example

```
## INSTALLATION
$> mkdir dumblr_blog && cd dumblr_blog

$> virtualenv env && source env/bin/activate
New python executables in ...

$> pip install dumblr
...
Cleaning up...

$> dumblr
Usage: dumblr [OPTIONS] COMMAND [ARGS]...

Options:
  --version
  --help     Show this message and exit.

Commands:
  diff    Generates diff report for updated posts
  init    Initialize dumblr directory
  load    Loads posts pulled from tumblr to fs
  new     Create new post
  pull    Pulls posts from Tumblr
  push    Pushes changes to Tumblr
  status  Checks status of posts in file system

## INITIALIZE DUMBLR DIRECTORY
$> dumblr init
Please register a Tumblr app to obtain OAuth keys
https://www.tumblr.com/oauth/apps
Consumer key: <paste your consumer key here>
Secret key: <paste your secret key here>

Please visit the following URL and authorize the app:
http://www.tumblr.com/oauth/authorize?oauth_token=foobar
Paste the URL of the redirected page: <redirect_url>?oauth_token=foobar

Initialized dumblr at ~/dumblr_blog/.dumblr

## PULL TEXT POSTS FROM TUMBLR BLOG
$> dumblr pull
# From blog <your blog>
#
#	Retrieved : test1.markdown
#	Retrieved : test2.markdown
#
# Total : 2

## LOAD PULLED POST TO YOUR FS
$> dumblr load
# Loading to ~/dumblr_blog/posts
#
#       test1.markdown
#       test2.markdown
#
# Total : 2

## POSTS ARE LOADED AS FILES (MARKDOWN OR HTML)
$> ls
env posts

$> ls posts/
test1.markdown test2.markdown

$> cat posts/test1.markdown
---
title: u'test1'
date: 2015-03-01 18:30:07 GMT
slug: test1
tags: []
format: markdown
state: draft
id: 123456789
---

hello world!

## CREATE NEW POST
$> dumblr new "test3"
# Created new post ~/dumblr_blog/posts/test3.markdown

$> cat posts/test3.markdown
---
title: test3
date: 2015-03-01 19:15:55.790696 GMT
slug: test3
tags: []
format: markdown
state: draft
id: -1
---

## OR A NEW HTML POST
$> dumblr new "test4" -f html
# Created new post ~/dumblr_blog/posts/test4.html

## check status of posts in fs
$> dumblr status
# Status on directory ~/dumblr_blog/posts
#
#	new post	: test3.markdown
#	new post	: test4.html
#

## MAKE CHANGES TO EXISTING POSTS
$> vim/emacs/subline/atom/etc test1.markdown ## changed body to "goodbye world!"

$> dumblr status
# Status on directory ~/dumblr_blog/posts
#
#	modified	: test1.markdown
#	new post	: test3.markdown
#	new post	: test4.html
#

## AND REVIEW WHAT CHANGED
$> dumblr diff
# Diff result:
#
test1.markdown

	body
	- hello world!
	+ goodbye world!
#

## NOW PUSH THE CHANGES BACK TO TUMBLR
$> dumblr push
# Push result:
#
#	True	: test1
#	True	: test3
#	True	: test4
#
```

## BUGS
- Bugs with unicode abound :(
- Bugs with yaml frontmatter abound :(
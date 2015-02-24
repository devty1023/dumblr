import click
import pytumblr
from requests_oauthlib import OAuth1Session

class Tumblr(object):
    def __init__(self, ckey, skey, oauth, oauth_s):
        self.tumblr = pytumblr.TumblrRestClient(ckey, 
                                                skey,
                                                oauth,
                                                oauth_s)

    def info(self):
        """Retrieves blog information of the token holder
        
        Filters out all but the following:
        - 'user' 'name'
        """
        d = self.tumblr.info()
        return {'name' : d['user']['name']}

    def get_text_posts(self, name):
        """Retrieves all text posts from tumblr, including drafts
        """
        pub_posts = self.tumblr.posts(name, type='text', filter='raw')['posts']
        draft_posts = self.tumblr.drafts(name, filter='raw')['posts']
        ## drafts api call cannot filter by type
        draft_posts = filter(lambda x : x['type'] == 'text', draft_posts)

        ## remove every key but
        keeps = ['body', 'date', 'format', 'slug', 'title', 'tags']
        pub_posts = [{keep : post[keep] for keep in keeps} for post in pub_posts]
        draft_posts = [{keep : post[keep] for keep in keeps} for post in draft_posts]

        ## include state 
        pub_posts = map(lambda x : dict(x, state='published'), pub_posts)
        draft_posts = map(lambda x : dict(x, state='draft'), draft_posts)
        
        return pub_posts + draft_posts

    @staticmethod
    def oauth(ckey=None, skey=None):
        """Retrieves OAuth tokens via OAuth 1.0 protocol

        returns a dictionary of retrieved tokens and application tokens
        """
        urls = {
            'request' : "http://www.tumblr.com/oauth/request_token",
            'authorize' : "http://www.tumblr.com/oauth/authorize",
            'access' : "http://www.tumblr.com/oauth/access_token"
        }

        if not ckey or not skey:
            click.secho("Please register a Tumblr app to obtain OAuth keys")
            click.secho("https://www.tumblr.com/oauth/apps", bold=True)
            ckey = click.prompt("Consumer key")
            skey = click.prompt("Secret key")
        
        oauth = OAuth1Session(ckey, client_secret=skey)
        resp = oauth.fetch_request_token(urls['request'])
        okey = resp.get('oauth_token')
        osecret = resp.get('oauth_token_secret')

        auth_url = oauth.authorization_url(urls['authorize'])
        click.secho("Please visit the following URL and authorize the app:")
        click.secho(auth_url, bold=True)
        resp = click.prompt("Paste the URL of the redirected page")
        oauth_response = oauth.parse_authorization_response(resp)
        verifier = oauth_response.get('oauth_verifier')

        oauth = OAuth1Session(ckey,
                              client_secret=skey,
                              resource_owner_key=okey,
                              resource_owner_secret=osecret,
                              verifier=verifier)
        tokens = oauth.fetch_access_token(urls["access"])
        tokens.update({'consumer_key' : ckey, 'secret_key' : skey})
        return tokens

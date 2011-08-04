from oauth import oauth
import time
import urlparse
import urllib2
from flickr_keys import API_KEY, API_SECRET

TOKEN_REQUEST_URL = "http://www.flickr.com/services/oauth/request_token"
AUTHORIZE_URL = "http://www.flickr.com/services/oauth/authorize"
ACCESS_TOKEN_URL = "http://www.flickr.com/services/oauth/access_token"

class AuthHandlerError(Exception):
    pass

class AuthHandler(object):
    def __init__(self,key = API_KEY, secret = API_SECRET, callback = " ", access_token_key = None, access_token_secret = None):
        self.key = key
        self.secret = secret
        params = {
            'oauth_timestamp': str(int(time.time())),
            'oauth_signature_method':"HMAC-SHA1",
            'oauth_version': "1.0",
            'oauth_callback': callback,
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_consumer_key': self.key
        }

        self.consumer = oauth.OAuthConsumer(key=self.key, secret=self.secret)
        if access_token_key is None :
            req = oauth.OAuthRequest(http_method="GET", http_url=TOKEN_REQUEST_URL, parameters=params)
            req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer,None)
            resp = urllib2.urlopen(req.to_url())
            request_token = dict(urlparse.parse_qsl(resp.read()))
            self.request_token = oauth.OAuthToken(request_token['oauth_token'],request_token['oauth_token_secret'])
            self.access_token = None
        else :
            self.request_token = None
            self.access_token = oauth.OAuthToken(access_token_key,access_token_secret) 
        

    def get_authorization_url(self,perms = 'read'):
        if self.request_token is None :
            raise AuthHandlerError("Request token is not defined. This ususally means that the access token has been loaded from a file.")
        return "%s?oauth_token=%s&perms=%s" % (AUTHORIZE_URL, self.request_token.key, perms)
    
    def set_verifier(self,oauth_verifier):
        if self.request_token is None :
            raise AuthHandlerError("Request token is not defined. This ususally means that the access token has been loaded from a file.")
        self.request_token.set_verifier(oauth_verifier)

        access_token_parms = {
            'oauth_consumer_key': self.key,
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_signature_method':"HMAC-SHA1",
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': self.request_token.key,
            'oauth_verifier' : self.request_token.verifier
        }

        req = oauth.OAuthRequest(http_method="GET", http_url=ACCESS_TOKEN_URL, parameters=access_token_parms)
        req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer,self.request_token)
        resp = urllib2.urlopen(req.to_url())
        access_token_resp = dict(urlparse.parse_qsl(resp.read()))
        self.access_token = oauth.OAuthToken(access_token_resp["oauth_token"],access_token_resp["oauth_token_secret"])

    def complete_parameters(self,url,params = {}):
        
        defaults = {
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': oauth.generate_nonce(),
            'signature_method': "HMAC-SHA1",
            'oauth_token':self.access_token.key,
            'oauth_consumer_key':self.consumer.key,
        }

        defaults.update(params)
        req = oauth.OAuthRequest(http_method="POST", http_url=url, parameters=defaults)
        req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer,self.access_token)
        return req

    def write(self,filename):
        if self.access_token is None :
            raise AuthHandlerError("Access token not set yet.")
        with open(filename,"w") as f :
            f.write("\n".join([self.key,self.secret,self.access_token.key,self.access_token.secret]))
            
    @staticmethod
    def load(filename):
        with open(filename,"r") as f :
            key,secret,access_key,access_secret = f.read().split("\n")
        return AuthHandler(key,secret,access_token_key = access_key,access_token_secret = access_secret)

        
        
        
    
    

from oauth import oauth
import time
import httplib2
import urlparse
import urllib2
from flickr_keys import API_KEY, API_SECRET

TOKEN_REQUEST_URL = "http://www.flickr.com/services/oauth/request_token"
AUTHORIZE_URL = "http://www.flickr.com/services/oauth/authorize"
ACCESS_TOKEN_URL = "http://www.flickr.com/services/oauth/access_token"

def token_request():
    params = {
        'oauth_timestamp': str(int(time.time())),
        'oauth_signature_method':"HMAC-SHA1",
        'oauth_version': "1.0",
        'oauth_callback': "http://www.flickr.com/",
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_consumer_key': API_KEY
    }

    consumer = oauth.OAuthConsumer(key=API_KEY, secret=API_SECRET)
    req = oauth.OAuthRequest(http_method="GET", http_url=TOKEN_REQUEST_URL, parameters=params)
    req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer,None)
    resp = urllib2.urlopen(req.to_url())
    request_token = dict(urlparse.parse_qsl(resp.read()))
    return request_token()

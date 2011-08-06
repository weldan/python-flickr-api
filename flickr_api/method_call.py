import urllib2
import urllib
import hashlib
import json

from base import FlickrError,FlickrAPIError
from flickr_keys import API_KEY, API_SECRET

REST_URL = "http://api.flickr.com/services/rest/"


def call_api(api_key = API_KEY, api_secret = API_SECRET, auth_handler = None, needssigning = False,url = REST_URL,exclude_signature = [],**args):
    clean_args(args)
    args["api_key"] = api_key
    args["format"] = 'json'
    args["nojsoncallback"] = 1
    if auth_handler is None :
        if needssigning :
            query_elements = [e.split("=") for e in query.split("&")]
            query_elements.sort()
            sig = API_SECRET+["".join(["".join(e) for e in query_elements])]
            m = hashlib.md5()
            m.update(sig)
            api_sig = m.digest()
            args["api_sig"] = api_sig
        data = urllib.urlencode(args)
        
    else :
         data = auth_handler.complete_parameters(url = url,params = args,exclude_signature = exclude_signature).to_postdata()

    req = urllib2.Request(url,data)
    

    try :
        resp = json.loads(urllib2.urlopen(req).read())
    except urllib2.HTTPError , e:
        raise FlickrError( e.read().split('&')[0] )



    if resp["stat"] != "ok" :
        raise FlickrAPIError(resp["code"],resp["message"])

    resp = clean_content(resp)

    return resp

def clean_content(d):
    if isinstance(d,dict):
        d_clean = {}
        if len(d) == 1 and d.has_key("_content") :
            return clean_content(d["_content"])
        for k,v in d.iteritems() :
            if k == "_content" :
                k = "text"
            d_clean[k] = clean_content(v)
        return d_clean
    elif isinstance(d,list):
        return [clean_content(i) for i in d]
    else :
        return d

def clean_args(args):
    for k,v in args.items() :
        if isinstance(v,bool):
            args[k] = int(v)

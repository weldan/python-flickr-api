
class FlickrError(Exception):
    pass

class FlickrAPIError(FlickrError):
    def __init__(self,code,message):
        FlickrError.__init__(self,"%i : %s"%(code,message))
        self.code = code
        self.message = message

class FlickrDictObject(object):
    def __init__(self,name,obj_dict):
        self.__name__ = name
        for k,v in obj_dict.iteritems() :
            if isinstance(v,dict) :
                v = FlickrDictObject(k,v)
            if isinstance(v,list) :
                v = [ FlickrDictObject(k,vi) for vi in v ]
            self.__dict__[k] = v

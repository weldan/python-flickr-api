
class FlickrError(Exception):
    pass

class FlickrAPIError(FlickrError):
    def __init__(self,code,message):
        FlickrError.__init__(self,"%i : %s"%(code,message))
        self.code = code
        self.message = message

class FlickrDictObject(object):
    """
        Tranform recursively JSON dictionnaries into objects
    """
    def __init__(self,name,obj_dict):
        self.__name__ = name
        for k,v in obj_dict.iteritems() :
            if isinstance(v,dict) :
                v = FlickrDictObject(k,v)
            if isinstance(v,list) :
                v = [ FlickrDictObject(k,vi) for vi in v ]
            self.__dict__[k] = v

class FlickrObject(object):
    """
        Base Object for Flickr API Objects
    """
    __converters__ = []
    __display__ = []
    
    def __init__(self,**params):
        params["loaded"] = False
        self._set_properties(**params)

    def _set_properties(self,**params):
        for c in self.__class__.__converters__ :
            c(params)
        self.__dict__.update(params)
    
    def __getattr__(self,name):
        if not self.loaded :
            self.load()
        if self.loaded : raise AttributeError("'%s' object has no attribute '%s'"%(self.__class__.__name__,name))
    
    def __setattr__(self,name,values):
        raise RunTimeError("Readonly attribute")
    
    def __str__(self):
        vals = []
        for k in self.__class__.__display__ :
            try :
                value = self.__dict__[k]
            except KeyError :
                self.load()
                value = self.__dict__[k]
            
            if isinstance(value,unicode):
                value = value.encode("utf8")
            if isinstance(value,str):
                value = "'%s'"%value
            else : value = str(value)
            vals.append("%s = %s"%(k,value))
        return "%s(%s)"%(self.__class__.__name__,",".join(vals))
    
    def __repr__(self): return str(self)

    def getInfo(self):
        """
            Returns object information as a dictionnary.
            Should be overriden.
        """
        if not hasattr(self,"id") : raise AttributeError("'%s' object has not attribute '%s'"%(self.__class__.__name__,"id"))
        return { "loaded" : True}

    def load(self):
        props = self.getInfo()
        self._set_properties(**props)

def dict_converter(keys,func):
    def convert(dict_) :
        for k in keys :
            try :
                dict_[k] = func(dict_[k])
            except KeyError : pass
    return convert

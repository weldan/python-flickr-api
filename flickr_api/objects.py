# -*- encoding: utf8 -*-
import method_call
import base

AUTH_HANDLER = None


class Test(object):
    @staticmethod
    def login():
        r = method_call.call_api(method = "flickr.test.login",auth_handler = AUTH_HANDLER)
        return r

def attr_getter(attr_name):
    def get(self):
        return self.__dict__["_%s__%s"%(self.__class__.__name__,attr_name)]


class FlickrObject(object):
    def __init__(self,object_id,**params):
        params["id"] = object_id
        params["loaded"] = False
        self._set_properties(**params)

    def _set_properties(self,**params):
        for k,v in params.iteritems() :
            self.__dict__[k] = v
    
    def __getattr__(self,name):
        if not self.loaded :
            self.load()
        if self.loaded : raise AttributeError("'%s' object has no attribute '%s'"%(self.__class__.__name__,name))
    
    def __setattr__(self,name,values):
        raise RunTimeError("Readonly attribute")

    def getInfo(self):
        """
            Returns object information as a dictionnary
        """
        return { "loaded" : True}
        
    def load(self):
        props = self.getInfo()
        self._set_properties(**props)
        
    
class Person(FlickrObject):
    
    @staticmethod
    def findByEmail(find_email):
        """
            method : flickr.people.findByEmail

            Return a user's NSID, given their email address
            
            Authentication: This method does not require authentication.
            
            Arguments :
                find_email (Required)
                    The email address of the user to find (may be primary or secondary).
                    
            Returns :
                The found user object
        """        
    
    @staticmethod
    def findByUserName(username):
        """
            method : flickr.people.findByUsername
            
            Return a user's NSID, given their username.
            
            Authentication :
                This method does not require authentication.
                
            Arguments :
                username (Required)
                    The username of the user to lookup. 

            Returns :
                The found user object.

            """
        r = method_call.call_api(method = "flickr.people.findByUsername", username = username,auth_handler = AUTH_HANDLER)
        user = r["user"]
        user["username"] = user["username"]["_content"]
        user_id = user.pop("id")
        user[u"object_id"] = user_id
        return Person(**user)
  
    def getPhotos(self,**args):
        """
            method = "flickr.people.getPhotos"
            
            Return photos from the given user's photostream. Only photos visible to the calling user will be returned. This method must be authenticated; to return public photos for a user, use flickr.people.getPublicPhotos.
            
            Authentification : Cette méthode exige une authentification avec autorisation de lecture.
            
            Arguments :
              safe_search (Facultatif)
                    Safe search setting:
                        * 1 for safe.
                        * 2 for moderate.
                        * 3 for restricted.
                    (Please note: Un-authed calls can only see Safe content.)

                min_upload_date (Facultatif)
                    Minimum upload date. Photos with an upload date greater than or equal to this value will be returned. The date should be in the form of a unix timestamp.
                max_upload_date (Facultatif)
                    Maximum upload date. Photos with an upload date less than or equal to this value will be returned. The date should be in the form of a unix timestamp.
                min_taken_date (Facultatif)
                    Minimum taken date. Photos with an taken date greater than or equal to this value will be returned. The date should be in the form of a mysql datetime.
                max_taken_date (Facultatif)
                    Maximum taken date. Photos with an taken date less than or equal to this value will be returned. The date should be in the form of a mysql datetime.
                content_type (Facultatif)
                    Content Type setting:

                        * 1 for photos only.
                        * 2 for screenshots only.
                        * 3 for 'other' only.
                        * 4 for photos and screenshots.
                        * 5 for screenshots and 'other'.
                        * 6 for photos and 'other'.
                        * 7 for photos, screenshots, and 'other' (all).

                privacy_filter (Facultatif)
                    Return photos only matching a certain privacy level. This only applies when making an authenticated call to view photos you own. Valid values are:

                        * 1 public photos
                        * 2 private photos visible to friends
                        * 3 private photos visible to family
                        * 4 private photos visible to friends & family
                        * 5 completely private photos

                extras (Facultatif)
                    A comma-delimited list of extra information to fetch for each returned record. Currently supported fields are: description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_m, url_z, url_l, url_o
                per_page (Facultatif)
                    Number of photos to return per page. If this argument is omitted, it defaults to 100. The maximum allowed value is 500.
                page (Facultatif)
                    The page of results to return. If this argument is omitted, it defaults to 1.
                    
            returns :
                (photo_list,info)
                photo_list is a list of Photo objects.
                info is a tuple with information about the request.
             
        """
        r = method_call.call_api(method = "flickr.people.getPhotos", user_id = self.id ,auth_handler = AUTH_HANDLER,**args)

        photoset = base.FlickrDictObject("photos",r["photos"])
        photos = []
        for p in  photoset.photo :
            photos.append(Photo(
                object_id = p.id,
                secret = p.secret,
                title = p.title,
                farm = p.farm,
                server = p.server,
                is_friend = bool(p.isfriend),
                is_public = bool(p.ispublic),
                is_family = bool(p.isfamily),
                owner = Person(p.owner)))
        return (photos,{
            'page' : photoset.page,
            'pages' : photoset.pages,
            'per_page' : photoset.perpage,
            'total' : photoset.total
            })
                
    
    def getPublicPhotos(self):
        """    method = "flickr.people.getPublicPhotos"
            
            Get a list of public photos for the given user.
        
            Authentification : Cette méthode n'exige pas d'authentification.

            Arguments :
              safe_search (Facultatif)
                    Safe search setting:

                        * 1 for safe.
                        * 2 for moderate.
                        * 3 for restricted.

                    (Please note: Un-authed calls can only see Safe content.)
                min_upload_date (Facultatif)
                    Minimum upload date. Photos with an upload date greater than or equal to this value will be returned. The date should be in the form of a unix timestamp.
                max_upload_date (Facultatif)
                    Maximum upload date. Photos with an upload date less than or equal to this value will be returned. The date should be in the form of a unix timestamp.
                min_taken_date (Facultatif)
                    Minimum taken date. Photos with an taken date greater than or equal to this value will be returned. The date should be in the form of a mysql datetime.
                max_taken_date (Facultatif)
                    Maximum taken date. Photos with an taken date less than or equal to this value will be returned. The date should be in the form of a mysql datetime.
                content_type (Facultatif)
                    Content Type setting:

                        * 1 for photos only.
                        * 2 for screenshots only.
                        * 3 for 'other' only.
                        * 4 for photos and screenshots.
                        * 5 for screenshots and 'other'.
                        * 6 for photos and 'other'.
                        * 7 for photos, screenshots, and 'other' (all).

                privacy_filter (Facultatif)
                    Return photos only matching a certain privacy level. This only applies when making an authenticated call to view photos you own. Valid values are:

                        * 1 public photos
                        * 2 private photos visible to friends
                        * 3 private photos visible to family
                        * 4 private photos visible to friends & family
                        * 5 completely private photos

                extras (Facultatif)
                    A comma-delimited list of extra information to fetch for each returned record. Currently supported fields are: description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_m, url_z, url_l, url_o
                per_page (Facultatif)
                    Number of photos to return per page. If this argument is omitted, it defaults to 100. The maximum allowed value is 500.
                page (Facultatif)
                    The page of results to return. If this argument is omitted, it defaults to 1.
                    
            returns :
                (photo_list,info)
                photo_list is a list of Photo objects.
                info is a tuple with information about the request.
        """
        r = method_call.call_api(method = "flickr.people.getPublicPhotos", user_id = self.id ,auth_handler = AUTH_HANDLER)
        photoset = base.FlickrDictObject("photos",r["photos"])
        photos = []
        for p in  photoset.photo :
            photos.append(Photo(
                object_id = p.id,
                secret = p.secret,
                title = p.title,
                farm = p.farm,
                server = p.server,
                is_friend = bool(p.isfriend),
                is_public = bool(p.ispublic),
                is_family = bool(p.isfamily),
                owner = Person(p.owner)))
        return (photos,{
            'page' : photoset.page,
            'pages' : photoset.pages,
            'per_page' : photoset.perpage,
            'total' : photoset.total
            })

    def getPhotosOf(self,owner):
        """ method :flickr.people.getPhotosOf
                Returns a list of photos containing a particular Flickr member.
                
            Authentication:
                This method does not require authentication.
                
            Arguments:
                owner_id (Optional)
                    An NSID of a Flickr member. This will restrict the list of photos to those taken by that member.
                extras (Optional)
                    A comma-delimited list of extra information to fetch for each returned record. Currently supported fields are: description, license, date_upload, date_taken, date_person_added, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_m, url_z, url_l, url_o
                per_page (Optional)
                    Number of photos to return per page. If this argument is omitted, it defaults to 100. The maximum allowed value is 500.
                page (Optional)
                    The page of results to return. If this argument is omitted, it defaults to 1. 
        """
        
        try :
            owner_id = owner.id
        except AttributeError :
            owner_id = id
        
        r = method_call.call_api(method = "flickr.people.getPhotosOf", user_id = self.id ,auth_handler = AUTH_HANDLER)
        photoset = base.FlickrDictObject("photos",r["photos"])
        photos = []
        for p in  photoset.photo :
            photos.append(Photo(
                object_id = p.id,
                secret = p.secret,
                title = p.title,
                farm = p.farm,
                server = p.server,
                is_friend = bool(p.isfriend),
                is_public = bool(p.ispublic),
                is_family = bool(p.isfamily),
                owner = Person(p.owner)))
        try :
            info = {
                'total' : photoset.total,
                'page' : photoset.page,
                'pages' : photoset.pages,
                'per_page' : photoset.perpage,
            }
        except AttributeError :
            info = {
                'page' : photoset.page,
                'per_page' : photoset.perpage,
                'has_next_page' : photoset.has_next_page
            }

        return (photos,info)

    def getPublicGroups(self,**args):
        """ method : flickr.people.getPublicGroups
                Returns the list of public groups a user is a member of.
              
            Authentication:
                This method does not require authentication.
            
            Arguments:
                invitation_only (Optional)
                    Include public groups that require an invitation or administrator approval to join. 
        """
        
        r = method_call.call_api(method = "flickr.people.getPublicGroups", user_id = self.id ,auth_handler = AUTH_HANDLER,**args)

        groups = base.FlickrDictObject("groups",r["groups"]).group
        
        groups_ = []
        for gr in groups :
            groups_.append(
                Group(
                    object_id = gr.nsid,
                    nsid = gr.nsid,
                    name = gr.name,
                    admin = bool(gr.admin),
                    eighteenplus = bool(gr.eighteenplus),
                    invitation_only = bool(gr.invitation_only)
                )
            )
        return groups_


class Tag(FlickrObject):
    pass

class Photo(FlickrObject):

    def getInfo(self):
        """
            method : flickr.photos.getInfo
        """
    
        r = method_call.call_api(method = "flickr.photos.getInfo", photo_id = self.id)
        photo = base.FlickrDictObject("photo",r["photo"])
        
        props = {
            'loaded' : True,
            'title' : photo.title,
            'description' : photo.description._content,
            'secret' : photo.secret,
            'farm' : photo.farm,
            'server' : photo.server,
            
            'owner' : Person(photo.owner.nsid,
                             nsid = photo.owner.nsid,
                             iconfarm = photo.owner.iconfarm,
                             iconserver = photo.owner.iconserver,
                             realname = photo.owner.realname,
                             username = photo.owner.username),
            'is_favorite' : int(photo.isfavorite),
            'date_uploaded' : int(photo.dateuploaded),
            
            'can_blog' : bool(photo.usage.canblog),
            'can_download' : bool(photo.usage.candownload),
            'can_print' : bool(photo.usage.canprint),
            'can_share' : bool(photo.usage.canshare),
            
            'nviews' : int(photo.views),
            'ncomments' : int(photo.comments._content),
            
            'is_family' : bool(photo.visibility.isfamily),
            'is_friend' : bool(photo.visibility.isfriend),
            'is_public' : bool(photo.visibility.ispublic),
            
            'can_add_meta' : bool(photo.publiceditability.canaddmeta),
            'can_comment ' : bool(photo.publiceditability.cancomment),
            'url' : photo.urls.url[0]._content,
            'rotation' : float(photo.rotation),
            'safety_level' : photo.safety_level,
       
            'tags' : [ Tag(t.id, value = t._content, author = Person(t.author), machine_tag = t.machine_tag, raw = t.raw) for t in photo.tags.tag ],
        }
        return props

    def addTags(self, tags):
        r = method_call.call_api(auth_handler = AUTH_HANDLER, method = "flickr.photos.addTags", photo_id = self.id)
        

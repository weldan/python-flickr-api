# -*- encoding: utf8 -*-
import method_call
import base

AUTH_HANDLER = None


class Test(object):
    @staticmethod
    def login():
        r = method_call.call_api(method = "flickr.test.login",auth_handler = AUTH_HANDLER)
        user = r["user"]
        return Person(user["id"],username = user["username"]["_content"])

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


    def getUploadStatus(self):
        """ method : flickr.people.getUploadStatus
            Returns information for the calling user related to photo uploads.
        
        Authentication:
            This method requires authentication with 'read' permission.
        """
        r = method_call.call_api(method = "flickr.people.getUploadStatus", user_id = self.id ,auth_handler = AUTH_HANDLER,**args)
        return r["user"]

    def getContactsPublicPhotos(self,**args):
        """ method: flickr.photos.getContactsPublicPhotos
            Fetch a list of recent public photos from a users' contacts.
            
        Authentication:
            This method does not require authentication.
        
        Arguments:
            count (Optional)
                Number of photos to return. Defaults to 10, maximum 50. This is only used if single_photo is not passed.
            just_friends (Optional)
                set as 1 to only show photos from friends and family (excluding regular contacts).
            single_photo (Optional)
                Only fetch one photo (the latest) per contact, instead of all photos in chronological order.
            include_self (Optional)
                Set to 1 to include photos from the user specified by user_id.
            extras (Optional)
                A comma-delimited list of extra information to fetch for each returned record. Currently supported fields are: license, date_upload, date_taken, owner_name, icon_server, original_format, last_update. 
        
        """
        r = method_call.call_api(method = "flickr.photos.getContactsPublicPhotos", user_id = self.id, auth_handler = AUTH_HANDLER,**args)
        photos = base.FlickrDictObject("photos",r["photos"]).photo
        photos_ = []
        for p in photos :
            props = {
                "id" : p.id ,
                "title" : p.title,
                "secret" : p.secret,
                "farm" : p.farm,
                "server" : p.server,
                "is_family" : p.isfamily,
                "is_friend" : p.isfriend,
                "is_public" : p.ispublic,
                "owner" : Person(p.owner,username = p.username)
            }
            photos_.append(Photo("",**props))
        return photos_
        
class Tag(FlickrObject):
    
    def remove(self):
        r = method_call.call_api(method = "flickr.photos.removeTag", tag_id = self.id,auth_handler = AUTH_HANDLER)
        return r

    

class Photo(FlickrObject):
    def addTags(self,tags):
         """ method : flickr.photos.addTags
                Add tags to a photo.
                
            Authentication:
                This method requires authentication with 'write' permission.

                Note: This method requires an HTTP POST request.
                
            Arguments:
                tags (Required)
                    The tags to add to the photo. 
                         
         """
         
         if isintance(tags,list):
             tags = ",".join(tags)
         
         r = method_call.call_api(method = "flickr.photos.addTags", photo_id = self.id, tags = tags,auth_handler = AUTH_HANDLER)
         return r
         
    def delete(self):
        """ method: flickr.photos.delete
            Delete a photo from flickr.
        
        Authentication:
            This method requires authentication with 'delete' permission.
            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.photos.delete", photo_id = self.id,auth_handler = AUTH_HANDLER)
        return r

    def getAllContexts(self):
        """ method: flickr.photos.getAllContexts
            Returns all visible sets and pools the photo belongs to.
        
        Authentication
            This method does not require authentication.

        """
        r = method_call.call_api(method = "flickr.photos.getAllContexts", photo_id = self.id,auth_handler = AUTH_HANDLER)
        photosets = []
        if r.has_key("set"):
            for s in r["set"]:
                photosets.append(PhotoSet("",**s))
        pools = []
        if r.has_key("pool"):
            for p in r["pool"]:
                pools.append(Pool("",**p))
                
            
        return photosets,pools
    
    @staticmethod
    def getContactsPhotos(**args):
        """ method: flickr.photos.getContactsPhotos
            Fetch a list of recent photos from the calling users' contacts.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            count (Optional)
                Number of photos to return. Defaults to 10, maximum 50. This is only used if single_photo is not passed.
            just_friends (Optional)
                set as 1 to only show photos from friends and family (excluding regular contacts).
            single_photo (Optional)
                Only fetch one photo (the latest) per contact, instead of all photos in chronological order.
            include_self (Optional)
                Set to 1 to include photos from the calling user.
            extras (Optional)
                A comma-delimited list of extra information to fetch for each returned record. Currently supported fields 
                include: license, date_upload, date_taken, owner_name, icon_server, original_format, last_update. For more
                information see extras under flickr.photos.search. 
        """
        r = method_call.call_api(method = "flickr.photos.getContactsPhotos", auth_handler = AUTH_HANDLER,**args)
        photos = base.FlickrDictObject("photos",r["photos"]).photo
        photos_ = []
        for p in photos :
            props = {
                "id" : p.id ,
                "title" : p.title,
                "secret" : p.secret,
                "farm" : p.farm,
                "server" : p.server,
                "is_family" : p.isfamily,
                "is_friend" : p.isfriend,
                "is_public" : p.ispublic,
                "owner" : Person(p.owner,username = p.username)
            }
            photos_.append(Photo("",**props))
        return photos_
    


    def getInfo(self):
        """
            method : flickr.photos.getInfo
        """
    
        r = method_call.call_api(method = "flickr.photos.getInfo", photo_id = self.id)
        photo = base.FlickrDictObject("photo",r["photo"])
        
        props = {
            'loaded' : True,
            'title' : photo.title._content,
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

    def getContext(self):
        """ method: flickr.photos.getContext
            Returns next and previous photos for a photo in a photostream.
        
        Authentication:
            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photos.getContext", photo_id = self.id,auth_handler = AUTH_HANDLER)

        return Photo("",**r["prevphoto"]),Photo("",**r["nextphoto"])

    @staticmethod
    def getCounts(**args):
        """ method: flickr.photos.getCounts
            Gets a list of photo counts for the given date ranges for the calling user.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            dates (Optional)
                A comma delimited list of unix timestamps, denoting the periods to return counts for. They should be specified smallest first.
            taken_dates (Optional)
                A comma delimited list of mysql datetimes, denoting the periods to return counts for. They should be specified smallest first. 
                    
        """
        r = method_call.call_api(method = "flickr.photos.getCounts", auth_handler = AUTH_HANDLER, **args)
        return r["photocounts"]["photocount"]

    def getExif(self):
        """ method: flickr.photos.getExif
            Retrieves a list of EXIF/TIFF/GPS tags for a given photo. The calling user must have permission to view the photo.
            
        Authentication:
            This method does not require authentication.
        """
        
        if hasattr(self,"secret"):
            r = method_call.call_api(method = "flickr.photos.getExif", photo_id = self.id, secret = self.secret)            
        else :
            r = method_call.call_api(method = "flickr.photos.getExif", photo_id = self.id, auth_handler = AUTH_HANDLER)
        return r["photo"]["exif"]
    
    def getFavorites(self,**args):
        """ method: flickr.photos.getFavorites
            Returns the list of people who have favorited a given photo.
            
        Authentication:
            This method does not require authentication.
        
        Arguments:
            page (Optional)
                The page of results to return. If this argument is omitted, it defaults to 1.
            per_page (Optional)
                Number of usres to return per page. If this argument is omitted, it defaults to 10. The maximum allowed value is 50.
        
        """
        r = method_call.call_api(method = "flickr.photos.getFavorites", photo_id = self.id,auth_handler = AUTH_HANDLER,**args)
        
        persons = []
        for p in r["photo"]["person"] :
            persons.append(Person(p["nsid"],**p))
        photo = r["photo"]
        infos = {
            "page" : photo["page"],
            "per_page" : photo["perpage"],
            "pages" : photo["pages"],
            "total" : photo["total"]
        }
        
        return persons,infos
        
    @staticmethod
    def getNotInSet(**args):
        """ method: flickr.photos.getNotInSet
            Returns a list of your photos that are not part of any sets.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            max_upload_date (Optional)
                Maximum upload date. Photos with an upload date less than
                or equal to this value will be returned. The date can be
                in the form of a unix timestamp or mysql datetime.
            min_taken_date (Optional)
                Minimum taken date. Photos with an taken date greater 
                than or equal to this value will be returned. The date
                can be in the form of a mysql datetime or unix timestamp.
            max_taken_date (Optional)
                Maximum taken date. Photos with an taken date less than 
                or equal to this value will be returned. The date can be
                in the form of a mysql datetime or unix timestamp.
            privacy_filter (Optional)
                Return photos only matching a certain privacy level. Valid 
                values are:

                    1 public photos
                    2 private photos visible to friends
                    3 private photos visible to family
                    4 private photos visible to friends & family
                    5 completely private photos

            media (Optional)
                Filter results by media type. Possible values are all 
                (default), photos or videos
            min_upload_date (Optional)
                Minimum upload date. Photos with an upload date greater 
                than or equal to this value will be returned. The date 
                can be in the form of a unix timestamp or mysql datetime.
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields are: 
                description, license, date_upload, date_taken, owner_name, 
                icon_server, original_format, last_update, geo, tags, 
                machine_tags, o_dims, views, media, path_alias, url_sq, 
                url_t, url_s, url_m, url_z, url_l, url_o
            per_page (Optional)
                Number of photos to return per page. If this argument is 
                omitted, it defaults to 100. The maximum allowed value is 
                500.
            page (Optional)
                The page of results to return. If this argument is 
                omitted, it defaults to 1. 
        """
        
        r = method_call.call_api(method = "flickr.photos.getNotInSet", auth_handler = AUTH_HANDLER,**args)

        return _extract_photo_list(r)


    @staticmethod
    def getRecent(**args):
        """ method: flickr.photos.getRecent -> photos,infos

            Returns a list of the latest public photos uploaded to flickr.
            
        Authentication:
            This method does not require authentication.
        
        Arguments:
            extras (Optional)
                A comma-delimited list of extra information to fetch for each returned record. Currently supported fields are: description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_m, url_z, url_l, url_o
            per_page (Optional)
                Number of photos to return per page. If this argument is omitted, it defaults to 100. The maximum allowed value is 500.
            page (Optional)
                The page of results to return. If this argument is omitted, it defaults to 1. 
                    
        """
        r = method_call.call_api(method = "flickr.photos.getRecent", auth_handler = AUTH_HANDLER,**args)
        
        return _extract_photo_list(r)
     

    def getSizes(self):
        """ method: flickr.photos.getSizes

            Returns the available sizes for a photo. The calling user must have permission to view the photo.
        
        Authentication:
            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photos.getSizes", photo_id, self.id, auth_handler = AUTH_HANDLER)
        
        return r["sizes"]["size"]
        
    @staticmethod
    def getUntagged(**args):
        """ method: flickr.photos.getUntagged -> photos,infos

            Returns a list of your photos with no tags.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            min_upload_date (Optional)
                Minimum upload date. Photos with an upload date greater 
                than or equal to this value will be returned. The date 
                can be in the form of a unix timestamp or mysql datetime.
            max_upload_date (Optional)
                Maximum upload date. Photos with an upload date less than 
                or equal to this value will be returned. The date can be 
                in the form of a unix timestamp or mysql datetime.
            min_taken_date (Optional)
                Minimum taken date. Photos with an taken date greater than 
                or equal to this value will be returned. The date should 
                be in the form of a mysql datetime or unix timestamp.
            max_taken_date (Optional)
                Maximum taken date. Photos with an taken date less than 
                or equal to this value will be returned. The date can be 
                in the form of a mysql datetime or unix timestamp.
            privacy_filter (Optional)
                Return photos only matching a certain privacy level. Valid 
                values are:

                    1 public photos
                    2 private photos visible to friends
                    3 private photos visible to family
                    4 private photos visible to friends & family
                    5 completely private photos

            media (Optional)
                Filter results by media type. Possible values are all 
                (default), photos or videos
            extras (Optional)
        
        
        """
        r = method_call.call_api(method = "flickr.photos.getUntagged", auth_handler = AUTH_HANDLER,**args)
            
        return _extract_photo_list(r)

    @staticmethod
    def getWithGeoData(**args):
        """ method: flickr.photos.getWithGeoData
            Returns a list of your geo-tagged photos.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            min_upload_date (Optional)
                Minimum upload date. Photos with an upload date greater 
                than or equal to this value will be returned. The date 
                should be in the form of a unix timestamp.
            max_upload_date (Optional)
                Maximum upload date. Photos with an upload date less than 
                or equal to this value will be returned. The date should 
                be in the form of a unix timestamp.
            min_taken_date (Optional)
                Minimum taken date. Photos with an taken date greater 
                than or equal to this value will be returned. The date 
                should be in the form of a mysql datetime.
            max_taken_date (Optional)
                Maximum taken date. Photos with an taken date less than 
                or equal to this value will be returned. The date should 
                be in the form of a mysql datetime.
            privacy_filter (Optional)
                Return photos only matching a certain privacy level. Valid 
                values are:

                    1 public photos
                    2 private photos visible to friends
                    3 private photos visible to family
                    4 private photos visible to friends & family
                    5 completely private photos

            sort (Optional)
                The order in which to sort returned photos. Deafults to 
                date-posted-desc. The possible values are: date-posted-asc, 
                date-posted-desc, date-taken-asc, date-taken-desc, 
                interestingness-desc, and interestingness-asc.
            media (Optional)
                Filter results by media type. Possible values are all 
                (default), photos or videos
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields are: 
                description, license, date_upload, date_taken, owner_name, 
                icon_server, original_format, last_update, geo, tags, 
                machine_tags, o_dims, views, media, path_alias, url_sq, 
                url_t, url_s, url_m, url_z, url_l, url_o
            per_page (Optional)
                Number of photos to return per page. If this argument is 
                omitted, it defaults to 100. The maximum allowed value is 
                500.
            page (Optional)
                The page of results to return. If this argument is 
                omitted, it defaults to 1.         
        """
        r = method_call.call_api(method = "flickr.photos.getWithGeoData", auth_handler = AUTH_HANDLER,**args)
            
        return _extract_photo_list(r)

    @staticmethod
    def getWithoutGeoData(**args):
        """ method: flickr.photos.getWithoutGeoData
            Returns a list of your photos which haven't been geo-tagged.
        
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            max_upload_date (Optional)
                Maximum upload date. Photos with an upload date less than 
                or equal to this value will be returned. The date should 
                be in the form of a unix timestamp.
            min_taken_date (Optional)
                Minimum taken date. Photos with an taken date greater 
                than or equal to this value will be returned. The date 
                can be in the form of a mysql datetime or unix timestamp.
            max_taken_date (Optional)
                Maximum taken date. Photos with an taken date less than 
                or equal to this value will be returned. The date can be 
                in the form of a mysql datetime or unix timestamp.
            privacy_filter (Optional)
                Return photos only matching a certain privacy level. 
                Valid values are:

                    1 public photos
                    2 private photos visible to friends
                    3 private photos visible to family
                    4 private photos visible to friends & family
                    5 completely private photos

            sort (Optional)
                The order in which to sort returned photos. Deafults to 
                date-posted-desc. The possible values are: date-posted-asc, 
                date-posted-desc, date-taken-asc, date-taken-desc, 4
                interestingness-desc, and interestingness-asc.
            media (Optional)
                Filter results by media type. Possible values are all 
                (default), photos or videos
            min_upload_date (Optional)
                Minimum upload date. Photos with an upload date greater 
                than or equal to this value will be returned. The date 
                can be in the form of a unix timestamp or mysql datetime.
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields are: 
                description, license, date_upload, date_taken, owner_name, 
                icon_server, original_format, last_update, geo, tags, 
                machine_tags, o_dims, views, media, path_alias, url_sq, 
                url_t, url_s, url_m, url_z, url_l, url_o
            per_page (Optional)
                Number of photos to return per page. If this argument is 
                omitted, it defaults to 100. The maximum allowed value is 
                500.
            page (Optional)
                The page of results to return. If this argument is omitted, 
                it defaults to 1.

        """
        r = method_call.call_api(method = "flickr.photos.getWithoutGeoData", auth_handler = AUTH_HANDLER,**args)
            
        return _extract_photo_list(r)

    @staticmethod
    def recentlyUpdated(**args):
        """ method: flickr.photos.recentlyUpdated

            Return a list of your photos that have been recently created 
            or which have been recently modified.

            Recently modified may mean that the photo's metadata (title, 
            description, tags) may have been changed or a comment has been 
            added (or just modified somehow :-)
        
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            min_date (Required)
                A Unix timestamp or any English textual datetime 
                description indicating the date from which modifications 
                should be compared.
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields are: 
                description, license, date_upload, date_taken, owner_name, 
                icon_server, original_format, last_update, geo, tags, 
                machine_tags, o_dims, views, media, path_alias, url_sq, 
                url_t, url_s, url_m, url_z, url_l, url_o
            per_page (Optional)
                Number of photos to return per page. If this argument is 
                omitted, it defaults to 100. The maximum allowed value 
                is 500.
            page (Optional)
                The page of results to return. If this argument is omitted, 
                it defaults to 1. 
        """
        r = method_call.call_api(method = "flickr.photos.recentlUpdated", auth_handler = AUTH_HANDLER,**args)
            
        return _extract_photo_list(r)

    @staticmethod
    def search(self,**args):
        """ method: flickr.photos.search
            Return a list of photos matching some criteria. Only photos visible to 
            the calling user will be returned. To return private or semi-private photos, the caller must be authenticated with 'read' permissions, and have permission to view the photos. Unauthenticated calls will only return public photos.
            
        Authentication:
            This method does not require authentication.
        
        Arguments:
            user_id (Optional)
                The NSID of the user who's photo to search. If this 
                parameter isn't passed then everybody's public photos 
                will be searched. A value of "me" will search against the 
                calling user's photos for authenticated calls.
            tags (Optional)
                A comma-delimited list of tags. Photos with one or more 
                of the tags listed will be returned. You can exclude results 
                that match a term by prepending it with a - character.
            tag_mode (Optional)
                Either 'any' for an OR combination of tags, or 'all' for 
                an AND combination. Defaults to 'any' if not specified.
            text (Optional)
                A free text search. Photos who's title, description or 
                tags contain the text will be returned. You can exclude 
                results that match a term by prepending it with a - character.
            min_upload_date (Optional)
                Minimum upload date. Photos with an upload date greater 
                than or equal to this value will be returned. The date can 
                be in the form of a unix timestamp or mysql datetime.
            max_upload_date (Optional)
                Maximum upload date. Photos with an upload date less than 
                or equal to this value will be returned. The date can be 
                in the form of a unix timestamp or mysql datetime.
            min_taken_date (Optional)
                Minimum taken date. Photos with an taken date greater 
                than or equal to this value will be returned. The date 
                can be in the form of a mysql datetime or unix timestamp.
            max_taken_date (Optional)
                Maximum taken date. Photos with an taken date less than 
                or equal to this value will be returned. The date can be 
                in the form of a mysql datetime or unix timestamp.
            license (Optional)
                The license id for photos (for possible values see the 
                flickr.photos.licenses.getInfo method). Multiple licenses 
                may be comma-separated.
            sort (Optional)
                The order in which to sort returned photos. Deafults to 
                date-posted-desc (unless you are doing a radial geo query, 
                in which case the default sorting is by ascending distance 
                from the point specified). The possible values are: 
                date-posted-asc, date-posted-desc, date-taken-asc, 
                date-taken-desc, interestingness-desc, interestingness-asc, 
                and relevance.
            privacy_filter (Optional)
                Return photos only matching a certain privacy level. This 
                only applies when making an authenticated call to view 
                photos you own. Valid values are:

                    1 public photos
                    2 private photos visible to friends
                    3 private photos visible to family
                    4 private photos visible to friends & family
                    5 completely private photos

            bbox (Optional)
                A comma-delimited list of 4 values defining the Bounding 
                Box of the area that will be searched.

                The 4 values represent the bottom-left corner of the box 
                and the top-right corner, minimum_longitude, minimum_latitude, 
                maximum_longitude, maximum_latitude.

                Longitude has a range of -180 to 180 , latitude of -90 
                to 90. Defaults to -180, -90, 180, 90 if not specified.

                Unlike standard photo queries, geo (or bounding box) 
                queries will only return 250 results per page.

                Geo queries require some sort of limiting agent in order 
                to prevent the database from crying. This is basically 
                like the check against "parameterless searches" for queries 
                without a geo component.

                A tag, for instance, is considered a limiting agent as 
                are user defined min_date_taken and min_date_upload 
                parameters — If no limiting factor is passed we return 
                only photos added in the last 12 hours (though we may 
                extend the limit in the future).

            accuracy (Optional)
                Recorded accuracy level of the location information. 
                Current range is 1-16 :

                    World level is 1
                    Country is ~3
                    Region is ~6
                    City is ~11
                    Street is ~16

                Defaults to maximum value if not specified.
            safe_search (Optional)
                Safe search setting:

                    1 for safe.
                    2 for moderate.
                    3 for restricted.

                (Please note: Un-authed calls can only see Safe content.)
            content_type (Optional)
                Content Type setting:

                    1 for photos only.
                    2 for screenshots only.
                    3 for 'other' only.
                    4 for photos and screenshots.
                    5 for screenshots and 'other'.
                    6 for photos and 'other'.
                    7 for photos, screenshots, and 'other' (all).

            machine_tags (Optional)
                Aside from passing in a fully formed machine tag, there 
                is a special syntax for searching on specific properties :

                    Find photos using the 'dc' namespace : "machine_tags" => "dc:"
                    Find photos with a title in the 'dc' namespace : "machine_tags" => "dc:title="
                    Find photos titled "mr. camera" in the 'dc' namespace : "machine_tags" => "dc:title=\"mr. camera\"
                    Find photos whose value is "mr. camera" : "machine_tags" => "*:*=\"mr. camera\""
                    Find photos that have a title, in any namespace : "machine_tags" => "*:title="
                    Find photos that have a title, in any namespace, whose value is "mr. camera" : "machine_tags" => "*:title=\"mr. camera\""
                    Find photos, in the 'dc' namespace whose value is "mr. camera" : "machine_tags" => "dc:*=\"mr. camera\""

                Multiple machine tags may be queried by passing a 
                comma-separated list. The number of machine tags you can 
                pass in a single query depends on the tag mode (AND or OR) 
                that you are querying with. "AND" queries are limited to 
                (16) machine tags. "OR" queries are limited to (8).
        
            machine_tag_mode (Optional)
                Either 'any' for an OR combination of tags, or 'all' for 
                an AND combination. Defaults to 'any' if not specified.
            group_id (Optional)
                The id of a group who's pool to search. If specified, 
                only matching photos posted to the group's pool will be 
                returned.
            contacts (Optional)
                Search your contacts. Either 'all' or 'ff' for just friends 
                and family. (Experimental)
            woe_id (Optional)
                A 32-bit identifier that uniquely represents spatial entities. 
                (not used if bbox argument is present).

                Geo queries require some sort of limiting agent in order 
                to prevent the database from crying. This is basically 
                like the check against "parameterless searches" for queries 
                without a geo component.

                A tag, for instance, is considered a limiting agent as 
                are user defined min_date_taken and min_date_upload 
                parameters — If no limiting factor is passed we return 
                only photos added in the last 12 hours (though we may e
                xtend the limit in the future).
        
            place_id (Optional)
                A Flickr place id. (not used if bbox argument is present).

                Geo queries require some sort of limiting agent in order 
                to prevent the database from crying. This is basically 
                like the check against "parameterless searches" for queries 
                without a geo component.

                A tag, for instance, is considered a limiting agent as 
                are user defined min_date_taken and min_date_upload 
                parameters — If no limiting factor is passed we return 
                only photos added in the last 12 hours (though we may extend 
                the limit in the future).
                
            media (Optional)
                Filter results by media type. Possible values are all 
                (default), photos or videos
            has_geo (Optional)
                Any photo that has been geotagged, or if the value is "0" 
                any photo that has not been geotagged.

                Geo queries require some sort of limiting agent in order 
                to prevent the database from crying. This is basically 
                like the check against "parameterless searches" for queries 
                without a geo component.

                A tag, for instance, is considered a limiting agent as 
                are user defined min_date_taken and min_date_upload 
                parameters — If no limiting factor is passed we return 
                only photos added in the last 12 hours (though we may 
                extend the limit in the future).
                
            geo_context (Optional)
                Geo context is a numeric value representing the photo's 
                geotagginess beyond latitude and longitude. For example, 
                you may wish to search for photos that were taken "indoors" 
                or "outdoors".

                The current list of context IDs is :

                    0, not defined.
                    1, indoors.
                    2, outdoors.

                Geo queries require some sort of limiting agent in order 
                to prevent the database from crying. This is basically 
                like the check against "parameterless searches" for queries 
                without a geo component.

                A tag, for instance, is considered a limiting agent as 
                are user defined min_date_taken and min_date_upload 
                parameters — If no limiting factor is passed we return 
                only photos added in the last 12 hours (though we may 
                extend the limit in the future).
                
            lat (Optional)
                A valid latitude, in decimal format, for doing radial geo 
                queries.

                Geo queries require some sort of limiting agent in order 
                to prevent the database from crying. This is basically like 
                the check against "parameterless searches" for queries 
                without a geo component.

                A tag, for instance, is considered a limiting agent as 
                are user defined min_date_taken and min_date_upload 
                parameters — If no limiting factor is passed we return 
                only photos added in the last 12 hours (though we may 
                extend the limit in the future).
                
            lon (Optional)
                A valid longitude, in decimal format, for doing radial 
                geo queries.

                Geo queries require some sort of limiting agent in order 
                to prevent the database from crying. This is basically 
                like the check against "parameterless searches" for queries 
                without a geo component.

                A tag, for instance, is considered a limiting agent as 
                are user defined min_date_taken and min_date_upload 
                parameters — If no limiting factor is passed we return 
                only photos added in the last 12 hours (though we may 
                extend the limit in the future).
                
            radius (Optional)
                A valid radius used for geo queries, greater than zero 
                and less than 20 miles (or 32 kilometers), for use with 
                point-based geo queries. The default value is 5 (km).
            radius_units (Optional)
                The unit of measure when doing radial geo queries. Valid 
                options are "mi" (miles) and "km" (kilometers). The default 
                is "km".
            is_commons (Optional)
                Limit the scope of the search to only photos that are part 
                of the Flickr Commons project. Default is false.
            in_gallery (Optional)
                Limit the scope of the search to only photos that are in 
                a gallery? Default is false, search all photos.
            is_getty (Optional)
                Limit the scope of the search to only photos that are for 
                sale on Getty. Default is false.
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields are: 
                description, license, date_upload, date_taken, owner_name, 
                icon_server, original_format, last_update, geo, tags, 
                machine_tags, o_dims, views, media, path_alias, url_sq, 
                url_t, url_s, url_m, url_z, url_l, url_o
            per_page (Optional)
                Number of photos to return per page. If this argument is 
                omitted, it defaults to 100. The maximum allowed value is 
                500.
            page (Optional)
                The page of results to return. If this argument is omitted, 
                it defaults to 1. 
                    
        """
        try :
            args['user_id'] = args['user_id'].id
        except KeyError : pass

        r = method_call.call_api(method = "flickr.photos.search", auth_handler = AUTH_HANDLER,**args)            
        return _extract_photo_list(r)

    def setContentType(self,**args):
        """ method: flickr.photos.setContentType
            Set the content type of a photo.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            content_type (Required)
                The content type of the photo. Must be one of: 1 for Photo, 
                2 for Screenshot, and 3 for Other.        
        """
        r = method_call.call_api(method = "flickr.photos.setContentType", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)            
        return r

    def setDates(self,**args):
        """ method: flickr.photos.setDates
            Set one or both of the dates for a photo.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            date_posted (Optional)
                The date the photo was uploaded to flickr (see the dates documentation)
            date_taken (Optional)
                The date the photo was taken (see the dates documentation)
            date_taken_granularity (Optional)
                The granularity of the date the photo was taken (see the dates documentation) 
        
        """
        r = method_call.call_api(method = "flickr.photos.setDates", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)            
        return r
        
    def setMeta(self,**args):
        """ method: flickr.photos.setMeta
            Set the meta information for a photo.
            
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            title (Required)
                The title for the photo.
            description (Required)
                The description for the photo. 
        """
        r = method_call.call_api(method = "flickr.photos.setMeta", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)            
        return r
    
    def setPerms(self,**args):
        """ method: flickr.photos.setPerms
            Set permissions for a photo.

        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            is_public (Required)
                1 to set the photo to public, 0 to set it to private.
            is_friend (Required)
                1 to make the photo visible to friends when private, 0 to not.
            is_family (Required)
                1 to make the photo visible to family when private, 0 to not.
            perm_comment (Required)
                who can add comments to the photo and it's notes. one of:
                0: nobody
                1: friends & family
                2: contacts
                3: everybody
            perm_addmeta (Required)
                who can add notes and tags to the photo. one of:
                0: nobody / just the owner
                1: friends & family
                2: contacts
                3: everybody                     
        """
        r = method_call.call_api(method = "flickr.photos.setPerms", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)            
        return r
        
    def setSafetyLevel(self,**args):
        """ method: flickr.photos.setSafetyLevel
            Set the safety level of a photo.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            safety_level (Optional)
                The safety level of the photo. Must be one of: 1 for Safe, 
                2 for Moderate, and 3 for Restricted.
            hidden (Optional)
                Whether or not to additionally hide the photo from public
                searches. Must be either 1 for Yes or 0 for No.                     
        """
        r = method_call.call_api(method = "flickr.photos.setSafetyLevel", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)            
        return r

    def setTags(self,tags):
        """ method: flickr.photos.setTags
            Set the tags for a photo.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            tags (Required)
                All tags for the photo (as a single space-delimited string).        
        """
        r = method_call.call_api(method = "flickr.photos.setTags", photo_id = self.id, auth_handler = AUTH_HANDLER,tags = tags)
        return r
        
        
 
def _extract_photo_list(r):
    photos = []
    infos = r["photos"]
    pp = infos.pop("photo")
    
    for p in pp :
        owner = Person(p["owner"])
        p["owner"] = owner
        photos.append( Photo("",**p))
        
    return photos,infos 
    

class Pool(FlickrObject):
    pass

class PhotoSet(FlickrObject):
    pass

class Group(FlickrObject):
    pass

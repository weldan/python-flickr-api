# -*- encoding: utf8 -*-
"""
    Object Oriented implementation of Flickr API.
    
    Important notes:
    - For consistency, the nameing of methods might differ from the name
      in the official API. Please check the method "docstring" to know
      what is the implemented method.
      
    - For methods which expect an object "id", either the 'id' string
      or the object itself can be used as argument. Similar consideration
      holds for lists of id's. 
      
      For instance if "photo_id" is expected you can give call the function
      with named argument "photo = PhotoObject" or with the id string 
      "photo_id = id_string".


    Author : Alexis Mignon (c)
    email  : alexis.mignon_at_gmail.com
    Date   : 05/08/2011
"""
import method_call
from  base import FlickrDictObject,FlickrObject,FlickrError,dict_converter

AUTH_HANDLER = None

class Activity(FlickrObject):
    @staticmethod
    def userPhotos(**args):
        """ method :flickr.activity.userPhotos
            Returns a list of recent activity on photos belonging to the calling user.
            Do not poll this method more than once an hour.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            timeframe (Optional)
                The timeframe in which to return updates for. This can be 
                specified in days ('2d') or hours ('4h'). The default 
                behaviour is to return changes since the beginning of the
                previous user session.
            per_page (Optional)
                Number of items to return per page. If this argument is 
                omitted, it defaults to 10. The maximum allowed value is 50.
            page (Optional)
                The page of results to return. If this argument is omitted, 
                it defaults to 1. 

        """
        
        r = method_call.call_api(method = "flickr.activity.userPhotos",auth_handler = AUTH_HANDLER,**args)
        
        items = _check_list(r["items"]["item"])
        activities = []
        for item in items :
            activity = item.pop("activity")
            item_type = item.pop(["type"])
            if item_type == "photo" :
                item = Photo(**item)
            elif item_type == "photoset" :
                item = PhotoSet(**item)
            events_ = []
            events = _check_list(activity["event"])
            for e in events :
                user = e["user"]
                username = e.pop("username")
                e["user"] = Person(id = user, username = username)
                e_type = e.pop("type")
                if e_type == "comment" :
                    if item_type == "photo" :
                        events_.append(PhotoComment(photo = item, **e))
                    elif item_type == "photoset" :
                        events_.append(PhotoSetComment(photoset = item, **e))
                elif e_type == 'note' :
                    events_.append(Note(photo = item,**e))
            activities.append( Activity(item = item, events = events) )
        return activities
    
    @staticmethod
    def userComments(**args):
        """ method: flickr.activity.userComments
            Returns a list of recent activity on photos commented on by 
            the calling user. Do not poll this method more than once an hour.
        
        Authentication:

            This method requires authentication with 'read' permission.
        
        Arguments:
            per_page (Optional)
                Number of items to return per page. If this argument is omitted, it defaults to 10. The maximum allowed value is 50.
            page (Optional)
                The page of results to return. If this argument is omitted, it defaults to 1. 
        
        """
        
        r = method_call.call_api(method = "flickr.activity.userComments",auth_handler = AUTH_HANDLER,**args)
        
        items = _check_list(r["items"]["item"])
        activities = []
        for item in items :
            activity = item.pop("activity")
            item_type = item.pop(["type"])
            if item_type == "photo" :
                item = Photo(**item)
            elif item_type == "photoset" :
                item = PhotoSet(**item)
            events_ = []
            events = _check_list(activity["event"])
            for e in events :
                user = e["user"]
                username = e.pop("username")
                e["user"] = Person(id = user, username = username)
                e_type = e.pop("type")
                if e_type == "comment" :
                    if item_type == "photo" :
                        events_.append(PhotoComment(photo = item, **e))
                    elif item_type == "photoset" :
                        events_.append(PhotoSetComment(photoset = item, **e))
                elif e_type == 'note' :
                    events_.append(Note(photo = item,**e))
            activities.append( Activity(item = item, events = events) )
        return activities

class Blog(FlickrObject):
    __display__ = ["id","name"]
    __converters__ = [
        dict_converter(["needspassword"],bool),
    ]
    @staticmethod
    def getList(**args):
        """ method: flickr.blogs.getList
            Get a list of configured blogs for the calling user.
        
        Authentication:

            This method requires authentication with 'read' permission.
        
        Arguments:
            service (Optional)
                Optionally only return blogs for a given service id. You 
                can get a list of from flickr.blogs.getServices().
        """
        
        try :
            args["service"] = args["service"].id
        except (KeyError,AttributeError): pass
        r = method_call.call_api(method = "flickr.photos.blogs.getList",auth_handler = AUTH_HANDLER,**args)
        return [ Blog(**b) for b in _check_list(r["blogs"]["blog"])]
        
    @staticmethod
    def getServices():
        """ method: flickr.blogs.getServices
        
            Return a list of Flickr supported blogging services
        
        Authentication:
            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photos.blogs.getServices")
        return [ BlogService(**s) for s in _check_list(r["services"]["service"]) ]

    def postPhoto(self,**args):
        """ method: flickr.blogs.postPhoto
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            photo_id (Required)
                The id of the photo to blog
            title (Required)
                The blog post title
            description (Required)
                The blog post body
            blog_password (Optional)
                The password for the blog (used when the blog does not have 
                a stored password).
            service (Optional)
                A Flickr supported blogging service. Instead of passing a 
                blog id you can pass a service id and we'll post to the first 
                blog of that service we find. 
        """
        
        try : args["photo_id"] = args.pop("photo").id
        except KeyError : pass
        r = method_call.call_api(method = "flickr.photos.blogs.getServices",auth_handler = AUTH_HANDLER,**args)

class BlogService(FlickrObject):
    __display__ = ["id","text"]    

class Collection(FlickrObject):
    __display__ = ["id","title"]
    def getInfo(self):
        """ method: flickr.collections.getInfo
            
            Returns information for a single collection. Currently can 
            only be called by the collection owner, this may change.
        
        Authentication:

            This method requires authentication with 'read' permission.
        """
        
        r = method_call.call_api(method = "flickr.collections.getInfo",collection_id = self.id,auth_handler = AUTH_HANDLER,**args)
        
        collection = r["collection"]
        icon_photos = _check_list(collection["iconphotos"]["photo"])
        photos = []
        for p in photos :
            p["owner"] = Person(p["owner"])
            photos.append(Photo(**p))
        collection["iconphotos"] = photos
        return Collection(**collection)
    
    @staticmethod
    def getTree(**args):
        """ method: flickr.collections.getTree
        
        Returns a tree (or sub tree) of collections belonging to a given user.
    
    Authentication:

        This method does not require authentication.
    
    Arguments:
        collection_id (Optional)
            The ID of the collection to fetch a tree for, or zero to fetch the root collection. Defaults to zero.
        user_id (Optional)
            The ID of the account to fetch the collection tree for. Deafults to the calling user. 
        
        """
        
        try : args["collection_id"] = args.pop("collection").id
        except KeyError : pass
        
        try : args["user_id"] = args.pop("user").id
        except KeyError : pass
        
        r = method_call.call_api(method = "flickr.collections.getTree",auth_handler = AUTH_HANDLER,**args)

        collections = _check_list(r["collections"])
        collections_ = []
        for c in collections :
            sets = _check_list(c.pop("set"))
            sets_ = [ PhotoSet(**s) for s in sets]
            collections_.append(Collection(sets = sets_,**c))
        return collections_

class Group(FlickrObject):
    __converters__ = [
        dict_converter(["members","privacy"],int),
        dict_converter(["admin","eighteenplus","invistation_only"],bool)
    ]
    __display__ = ["id","name"]
    pass


class Info(FlickrObject):
    __converters__ = [
        dict_converter(["page","perpage","pages","total"],int)
    
    ]
    __display__ = ["page","perpage","pages","total"]
    pass

class Licence(FlickrObject):
    __display__ = ["id","name"]
    
    @staticmethod
    def getList():
        """ method: flickr.photos.licenses.getInfo
        
        Fetches a list of available photo licenses for Flickr.
        
    Authentication:
        This method does not require authentication.
        """

        r = method_call.call_api(method = "flickr.photos.licences.getInfo")
        licences = r["licences"]["licence"]
        if not isinstance(licences):
            licences = [licences]
        return [Licence(**l) for l in licences]

class Location(FlickrObject):
    __display__ = ["latitude","longitude","accuracy"]
    __converters__ = [
        dict_converter(["latitude","longitude"],float),
        dict_converter(["accuracy"],int),
    ]


class Note(FlickrObject):
    __display__ = ["id","text"]
    def edit(self,**args):
        """ method: flickr.photos.notes.edit
            Edit a note on a photo. Coordinates and sizes are in pixels, based on the 500px image size shown on individual photo pages.
            
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
    
        Arguments:
            note_x (Required)
                The left coordinate of the note
            note_y (Required)
                The top coordinate of the note
            note_w (Required)
                The width of the note
            note_h (Required)
                The height of the note
            note_text (Required)
                The description of the note 
        
        """
        r = method_call.call_api(method = "flickr.photos.notes.edit",node_id = self.id,auth_handler = AUTH_HANDLER,**args)
        return r
    
    def delete(self):
        """ method :flickr.photos.notes.delete
            Delete a note from a photo.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.photos.notes.delete",node_id = self.id,auth_handler = AUTH_HANDLER,**args)
        return r

class Person(FlickrObject):
    __converters__ = [
        dict_converter(["ispro"],bool),
    ]
    __display__ = ["id","username"]
    @staticmethod
    def findByEmail(find_email):
        """
            method : flickr.people.findByEmail

            Return a user's NSID, given their email address
            
            Authentication: This method does not require authentication.
            
            Arguments :
                find_email (Required)
                    The email address of the user to find (may be primary 
                    or secondary).
                    
            Returns :
                The found user object
        """        
        r = method_call.call_api(method = "flickr.people.findByEmail", find_email = find_email,auth_handler = AUTH_HANDLER)
        return Person(**r["user"])

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
        return Person(**r["user"])

    def getInfo(self,**args):
        
        r = method_call.call_api(method = "flickr.people.getInfo", user_id = self.id ,auth_handler = AUTH_HANDLER)

        user = r["person"]
        user["photos"] = FlickrDictObject("person",user["photos"])
        return user

    def getPhotos(self,**args):
        """
            method = "flickr.people.getPhotos"
            
                Return photos from the given user's photostream. Only photos 
                visible to the calling user will be returned. This method must 
                be authenticated; to return public photos for a user, use 
                flickr.people.getPublicPhotos.
            
            Authentification : Cette méthode exige une authentification avec 
            autorisation de lecture.
            
            Arguments :
              safe_search (Facultatif)
                    Safe search setting:
                        * 1 for safe.
                        * 2 for moderate.
                        * 3 for restricted.
                    (Please note: Un-authed calls can only see Safe content.)

                min_upload_date (Facultatif)
                    Minimum upload date. Photos with an upload date greater 
                    than or equal to this value will be returned. The date 
                    should be in the form of a unix timestamp.
                max_upload_date (Facultatif)
                    Maximum upload date. Photos with an upload date less 
                    than or equal to this value will be returned. The date 
                    should be in the form of a unix timestamp.
                min_taken_date (Facultatif)
                    Minimum taken date. Photos with an taken date greater 
                    than or equal to this value will be returned. The date 
                    should be in the form of a mysql datetime.
                max_taken_date (Facultatif)
                    Maximum taken date. Photos with an taken date less than 
                    or equal to this value will be returned. The date should 
                    be in the form of a mysql datetime.
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
                    Return photos only matching a certain privacy level. 
                    This only applies when making an authenticated call 
                    to view photos you own. Valid values are:

                        * 1 public photos
                        * 2 private photos visible to friends
                        * 3 private photos visible to family
                        * 4 private photos visible to friends & family
                        * 5 completely private photos

                extras (Facultatif)
                    A comma-delimited list of extra information to fetch 
                    for each returned record. Currently supported fields 
                    are: description, license, date_upload, date_taken, 
                    owner_name, icon_server, original_format, last_update, 
                    geo, tags, machine_tags, o_dims, views, media, path_alias, 
                    url_sq, url_t, url_s, url_m, url_z, url_l, url_o
                per_page (Facultatif)
                    Number of photos to return per page. If this argument 
                    is omitted, it defaults to 100. The maximum allowed 
                    value is 500.
                page (Facultatif)
                    The page of results to return. If this argument is 
                    omitted, it defaults to 1.
                    
            returns :
                (photo_list,info)
                photo_list is a list of Photo objects.
                info is a tuple with information about the request.
             
        """
        r = method_call.call_api(method = "flickr.people.getPhotos", user_id = self.id ,auth_handler = AUTH_HANDLER,**args)

        return _extract_photo_list(r)

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
                    Minimum upload date. Photos with an upload date greater 
                    than or equal to this value will be returned. The date 
                    should be in the form of a unix timestamp.
                max_upload_date (Facultatif)
                    Maximum upload date. Photos with an upload date less 
                    than or equal to this value will be returned. The date 
                    should be in the form of a unix timestamp.
                min_taken_date (Facultatif)
                    Minimum taken date. Photos with an taken date greater 
                    than or equal to this value will be returned. The date 
                    should be in the form of a mysql datetime.
                max_taken_date (Facultatif)
                    Maximum taken date. Photos with an taken date less than 
                    or equal to this value will be returned. The date should 
                    be in the form of a mysql datetime.
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
                    Return photos only matching a certain privacy level. 
                    This only applies when making an authenticated call 
                    to view photos you own. Valid values are:

                        * 1 public photos
                        * 2 private photos visible to friends
                        * 3 private photos visible to family
                        * 4 private photos visible to friends & family
                        * 5 completely private photos

                extras (Facultatif)
                    A comma-delimited list of extra information to fetch 
                    for each returned record. Currently supported fields 
                    are: description, license, date_upload, date_taken, 
                    owner_name, icon_server, original_format, last_update, 
                    geo, tags, machine_tags, o_dims, views, media, path_alias, 
                    url_sq, url_t, url_s, url_m, url_z, url_l, url_o
                per_page (Facultatif)
                    Number of photos to return per page. If this argument 
                    is omitted, it defaults to 100. The maximum allowed 
                    value is 500.
                page (Facultatif)
                    The page of results to return. If this argument is 
                    omitted, it defaults to 1.
                    
            returns :
                (photo_list,info)
                photo_list is a list of Photo objects.
                info is a tuple with information about the request.
        """
        r = method_call.call_api(method = "flickr.people.getPublicPhotos", user_id = self.id ,auth_handler = AUTH_HANDLER)
        return _extract_photo_list(r)

    def getPhotosOf(self,owner):
        """ method :flickr.people.getPhotosOf
                Returns a list of photos containing a particular Flickr 
                member.
                
            Authentication:
                This method does not require authentication.
                
            Arguments:
                owner_id (Optional)
                    An NSID of a Flickr member. This will restrict the list 
                    of photos to those taken by that member.
                extras (Optional)
                    A comma-delimited list of extra information to fetch 
                    for each returned record. Currently supported fields 
                    are: description, license, date_upload, date_taken, 
                    date_person_added, owner_name, icon_server, 
                    original_format, last_update, geo, tags, machine_tags, 
                    o_dims, views, media, path_alias, url_sq, url_t, url_s, 
                    url_m, url_z, url_l, url_o
                per_page (Optional)
                    Number of photos to return per page. If this argument 
                    is omitted, it defaults to 100. The maximum allowed 
                    value is 500.
                page (Optional)
                    The page of results to return. If this argument is 
                    omitted, it defaults to 1. 
        """
        
        try :
            owner_id = owner.id
        except AttributeError :
            owner_id = id
        
        r = method_call.call_api(method = "flickr.people.getPhotosOf", user_id = self.id ,auth_handler = AUTH_HANDLER)
        return _extract_photo_list(r)

    def getPublicGroups(self,**args):
        """ method : flickr.people.getPublicGroups
                Returns the list of public groups a user is a member of.
              
            Authentication:
                This method does not require authentication.
            
            Arguments:
                invitation_only (Optional)
                    Include public groups that require an invitation or 
                    administrator approval to join. 
        """
        
        r = method_call.call_api(method = "flickr.people.getPublicGroups", user_id = self.id ,auth_handler = AUTH_HANDLER,**args)

        groups = r["groups"]["group"]
        
        groups_ = []
        for gr in groups :
            gr["id"] = gr["nsid"]
            groups_.append(Group(**gr))
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
                Number of photos to return. Defaults to 10, maximum 50. 
                This is only used if single_photo is not passed.
            just_friends (Optional)
                set as 1 to only show photos from friends and family 
                (excluding regular contacts).
            single_photo (Optional)
                Only fetch one photo (the latest) per contact, instead 
                of all photos in chronological order.
            include_self (Optional)
                Set to 1 to include photos from the user specified by 
                user_id.
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields are: license, 
                date_upload, date_taken, owner_name, icon_server, 
                original_format, last_update. 
        
        """
        r = method_call.call_api(method = "flickr.photos.getContactsPublicPhotos", user_id = self.id, auth_handler = AUTH_HANDLER,**args)
        return _extract_photo_list(r)

class Tag(FlickrObject):
    
    def remove(self):
        r = method_call.call_api(method = "flickr.photos.removeTag", tag_id = self.id,auth_handler = AUTH_HANDLER)
        return r


class Photo(FlickrObject):
    __converters__ = [
        dict_converter(["isfamily","ispublic","isfriend","cancomment","canaddmeta","permcomment","permmeta","isfavorite"],bool),
        dict_converter(["posted","lastupdate"],int),
        dict_converter(["views","comments"],int),
    ]
    __display__ = ["id","title"]
    
    def addComment(self,**args):
        """ method: flickr.photos.comments.addComment
        
            Add comment to a photo as the currently authenticated user.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.

        Arguments:
            comment_text (Required)
                Text of the comment 
        """

        r = method_call.call_api(method = "flickr.photos.comments.addComment", photo_id = self.id,auth_handler = AUTH_HANDLER,**args)
        args["id"] = r["comment"]["id"]
        args["photo"] = self
        return PhotoComment(**args)

    def addNote(self,**args):
        """ method: flickr.photos.notes.add
            Add a note to a photo. Coordinates and sizes are in pixels, 
            based on the 500px image size shown on individual photo pages.
            
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            note_x (Required)
                The left coordinate of the note
            note_y (Required)
                The top coordinate of the note
            note_w (Required)
                The width of the note
            note_h (Required)
                The height of the note
            note_text (Required)
                The description of the note 
        """
        r = method_call.call_api(method = "flickr.photos.notes.add", photo_id = self.id,auth_handler = AUTH_HANDLER,**args)
        args["id"] = r["note"]["id"]
        args["photo"] = self
        return Note(**args)

    def addPerson(self,**args):
        """ method: flickr.photos.people.add
        
            Add a person to a photo. Coordinates and sizes of boxes are 
            optional; they are measured in pixels, based on the 500px image 
            size shown on individual photo pages.
            
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            user_id (Required)
                The NSID of the user to add to the photo.
            person_x (Optional)
                The left-most pixel co-ordinate of the box around the person.
            person_y (Optional)
                The top-most pixel co-ordinate of the box around the person.
            person_w (Optional)
                The width (in pixels) of the box around the person.
            person_h (Optional)
                The height (in pixels) of the box around the person. 
        """
        try :
            user_id = args.pop("user_id").id
        except KeyError :
            user_id = args["user_id"]

        r = method_call.call_api(method = "flickr.photos.people.add", photo_id = self.id, user_id = user_id,auth_handler = AUTH_HANDLER,**args)
        return PhotoPerson(id = user_id,**args)

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

    @staticmethod
    def batchCorrectLocation(**args):
        """ method: flickr.photos.geo.batchCorrectLocation
            Correct the places hierarchy for all the photos for a user at 
            a given latitude, longitude and accuracy.

            Batch corrections are processed in a delayed queue so it may 
            take a few minutes before the changes are reflected in a user's 
            photos.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            lat (Required)
                The latitude of the photos to be update whose valid range 
                is -90 to 90. Anything more than 6 decimal places will 
                be truncated.
            lon (Required)
                The longitude of the photos to be updated whose valid range 
                is -180 to 180. Anything more than 6 decimal places will 
                be truncated.
            accuracy (Required)
                Recorded accuracy level of the photos to be updated. World 
                level is 1, Country is ~3, Region ~6, City ~11, Street ~16. 
                Current range is 1-16. Defaults to 16 if not specified.
            place_id (Optional)
                A Flickr Places ID. (While optional, you must pass either 
                a valid Places ID or a WOE ID.)
            woe_id (Optional)
                A Where On Earth (WOE) ID. (While optional, you must pass 
                either a valid Places ID or a WOE ID.)                     
        """
        
        try :
            place = args.pop("place")
            if isinstance(place,Place):
                args["place_id"] = place.id
            else :
                args["place_id"] = place
        except KeyError : pass
        r = method_call.call_api(method = "flickr.photos.geo.batchCorrectLocation", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)

    def correctLocation(self,**args):
        """ method: flickr.photos.geo.correctLocation
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            place_id (Optional)
                A Flickr Places ID. (While optional, you must pass either 
                a valid Places ID or a WOE ID.)
            woe_id (Optional)
                A Where On Earth (WOE) ID. (While optional, you must pass 
                either a valid Places ID or a WOE ID.)
      
        """
        try :
            place = args.pop("place")
            if isinstance(place,Place):
                args["place_id"] = place.id
            else :
                args["place_id"] = place
        except KeyError : pass
        r = method_call.call_api(method = "flickr.photos.geo.batchCorrectLocation", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)

    @staticmethod
    def checkUploadTickets(self,tickets):
        """ method: flickr.photos.upload.checkTickets
        
            Checks the status of one or more asynchronous photo upload tickets.
        
        Authentication:

            This method does not require authentication.
        
        Arguments:
            tickets (Required)
                A comma-delimited list of ticket ids
        """
        if isinstance(tickets,list):
            tickets = [ t.id if isinstance(t,UploadTicket) else t for t in tickets]
        tickets = ",".joint(tickets)
        
        r = method_call.call_api(method = "flickr.photos.upload.checkTickets")
        tickets = r["wrapper"]["uploader"]["ticket"]
        if not isinstance(tickets,list):
            tickets = [tickets]
        return [UploadTicket(**t) for t in tickets]

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
                photosets.append(PhotoSet(**s))
        pools = []
        if r.has_key("pool"):
            for p in r["pool"]:
                pools.append(Pool(**p))

        return photosets,pools
    
    def getCommentList(self,**args):
        """ method: flickr.photos.comments.getList
            Returns the comments for a photo
        
        Authentication:
            This method does not require authentication.
        
        Arguments:
            min_comment_date (Optional)
                Minimum date that a a comment was added. The date should 
                be in the form of a unix timestamp.
            max_comment_date (Optional)
                Maximum date that a comment was added. The date should be 
                in the form of a unix timestamp. 
        """
        r = method_call.call_api(method = "flickr.photos.comments.getList", photo_id = self.id,auth_handler = AUTH_HANDLER,**args)
        comments = r["comments"]["comment"]
        comments_ = []
        if not isinstance(comments,list):
            comments = [comments]
        for c in comments :
            author = c["author"]
            authorname = c.pop("authorname")
            c["author"] = Person(id = author,username = authorname)
            comments_.append(PhotoComment(photo = self,**c))
        return comments_

    @staticmethod
    def getContactsPhotos(**args):
        """ method: flickr.photos.getContactsPhotos
            Fetch a list of recent photos from the calling users' contacts.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            count (Optional)
                Number of photos to return. Defaults to 10, maximum 50. 
                This is only used if single_photo is not passed.
            just_friends (Optional)
                set as 1 to only show photos from friends and family 
                (excluding regular contacts).
            single_photo (Optional)
                Only fetch one photo (the latest) per contact, instead of 
                all photos in chronological order.
            include_self (Optional)
                Set to 1 to include photos from the calling user.
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields 
                include: license, date_upload, date_taken, owner_name, 
                icon_server, original_format, last_update. For more
                information see extras under flickr.photos.search. 
        """
        r = method_call.call_api(method = "flickr.photos.getContactsPhotos", auth_handler = AUTH_HANDLER,**args)
        photos = r["photos"]["photo"]
        photos_ = []
        for p in photos :
            photos_.append(Photo(**p))
        return photos_
    
    def getInfo(self):
        """
            method : flickr.photos.getInfo
        """
    
        r = method_call.call_api(method = "flickr.photos.getInfo", photo_id = self.id)
        photo = r["photo"]
        
        owner = photo["owner"]
        owner["id"] = owner["nsid"]
        photo["owner"] = Person(**owner)
        
        photo.update(photo.pop("usage"))
        photo.update(photo.pop("visibility"))
        photo.update(photo.pop("publiceditability"))
        photo.update(photo.pop("dates"))
        
        tags = []
        for t in _check_list(photo["tags"]["tag"])  :
            t["author"] = Person(id = t.pop("author"))
            tags.append(Tag(**t))
            
        photo["tags"] = tags        
        notes = [Note(**n) for n in _check_list(photo["notes"]["note"])]
        
        return photo

    def getContext(self):
        """ method: flickr.photos.getContext
            Returns next and previous photos for a photo in a photostream.
        
        Authentication:
            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photos.getContext", photo_id = self.id,auth_handler = AUTH_HANDLER)

        return Photo(**r["prevphoto"]),Photo("",**r["nextphoto"])

    @staticmethod
    def getCounts(**args):
        """ method: flickr.photos.getCounts
            Gets a list of photo counts for the given date ranges for 
            the calling user.
            
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            dates (Optional)
                A comma delimited list of unix timestamps, denoting the 
                periods to return counts for. They should be specified 
                smallest first.
            taken_dates (Optional)
                A comma delimited list of mysql datetimes, denoting the 
                periods to return counts for. They should be specified 
                smallest first. 
                    
        """
        r = method_call.call_api(method = "flickr.photos.getCounts", auth_handler = AUTH_HANDLER, **args)
        return r["photocounts"]["photocount"]

    def getExif(self):
        """ method: flickr.photos.getExif
            Retrieves a list of EXIF/TIFF/GPS tags for a given photo. 
            The calling user must have permission to view the photo.
            
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
                The page of results to return. If this argument is omitted, 
                it defaults to 1.
            per_page (Optional)
                Number of users to return per page. If this argument is 
                omitted, it defaults to 10. The maximum allowed value is 50.
        """

        r = method_call.call_api(method = "flickr.photos.getFavorites", photo_id = self.id,auth_handler = AUTH_HANDLER,**args)
        
        
        photo = r["photo"]
        persons = photo.pop("person")
        persons_ = []
        if not isinstance(persons,list):
            persons = [persons]
        for p in r["photo"]["person"] :
            p["id"] = p["nsid"]
            persons_.append(Person(**p))
        infos = FlickrDictObject(photo)
        return persons_,infos
    
    def getGeoPerms(self):
        """ method: flickr.photos.geo.getPerms
        
            Get permissions for who may view geo data for a photo.
        
        Authentication:
            This method requires authentication with 'read' permission.
        """
        
        r = method_call.call_api(method = "flickr.photos.geo.getPerms", photo_id = self.id,auth_handler = AUTH_HANDLER)
        return GeoPerms(r["perms"])

    def getLocation(self):
        """ method: flickr.photos.geo.getLocation
            Get the geo data (latitude and longitude and the accuracy 
            level) for a photo.
            
        Authentication:
            This method does not require authentication.
        
        """
        r = method_call.call_api(method = "flickr.photos.geo.getLocation", photo_id = self.id)
        loc = r["photo"]["location"]
        return Location(photo = self, **loc)

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
        r = method_call.call_api(method = "flickr.photos.getRecent", auth_handler = AUTH_HANDLER,**args)
        
        return _extract_photo_list(r)
     

    def getSizes(self):
        """ method: flickr.photos.getSizes

            Returns the available sizes for a photo. The calling user must 
            have permission to view the photo.
        
        Authentication:
            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photos.getSizes", photo_id = self.id, auth_handler = AUTH_HANDLER)
        
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

    def getPeopleList(self,**args):
        """ method: flickr.photos.people.getList
            Get a list of people in a given photo.
            
        Authentication:
            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photos.people", auth_handler = AUTH_HANDLER,**args)
        
        info = r["people"]
        people = info.pop("person")
        people_ = []
        if not isinstance(people,Person):
            people = [people]
        for p in people :
            p["id"] = p["nsid"]
            p["photo"] = self
            people_.append(PhotoPerson(**p))
        return people_

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
    
    def removeLocation(self):
        """ method: flickr.photos.geo.removeLocation
            Removes the geo data associated with a photo.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.photos.geo.removeLocation",photo_id = self.id, auth_handler = AUTH_HANDLER,**args)

    def rotate(self,degrees):
        """ method:flickr.photos.transform.rotate
            Rotate a photo.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            degrees (Required)
                The amount of degrees by which to rotate the photo (clockwise)
                from it's current orientation. Valid values are 90, 180 and 270.
        """

        r = method_call.call_api(method = "flickr.photos.geo.removeLocation",photo_id = self.id, degrees = degrees, auth_handler = AUTH_HANDLER)
        photo_id  = r["photo_id"]["_content"]
        photo_secret = r["photo_id"]["secret"]
        return Photo(id = photo_id, secret = photo_secret)

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

    def setContext(self,context):
        """ method: flickr.photos.geo.setContext
            Indicate the state of a photo's geotagginess beyond latitude 
            and longitude.

            Note : photos passed to this method must already be geotagged 
            (using the "flickr.photos.geo.setLocation" method).
            
        Authentication:

            This method requires authentication with 'write' permission.
            Note: This method requires an HTTP POST request.
        
        Arguments:
            context (Required)
                Context is a numeric value representing the photo's 
                geotagginess beyond latitude and longitude. For example, 
                you may wish to indicate that a photo was taken "indoors" 
                or "outdoors".

                The current list of context IDs is :

                    * 0, not defined.
                    * 1, indoors.
                    * 2, outdoors.

        """
        r = method_call.call_api(method = "flickr.photos.search", photo_id = self.id, context = context, auth_handler = AUTH_HANDLER)
    
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
                The date the photo was uploaded to flickr (see the dates 
                documentation)
            date_taken (Optional)
                The date the photo was taken (see the dates documentation)
            date_taken_granularity (Optional)
                The granularity of the date the photo was taken (see the 
                dates documentation) 
        
        """
        r = method_call.call_api(method = "flickr.photos.setDates", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)
    
    def setGeoPerms(self,**args):
        """ method: flickr.photos.geo.setPerms

            Set the permission for who may view the geo data associated 
            with a photo.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            is_public (Required)
                1 to set viewing permissions for the photo's location data 
                to public, 0 to set it to private.
            is_contact (Required)
                1 to set viewing permissions for the photo's location data 
                to contacts, 0 to set it to private.
            is_friend (Required)
                1 to set viewing permissions for the photo's location data 
                to friends, 0 to set it to private.
            is_family (Required)
                1 to set viewing permissions for the photo's location data 
                to family, 0 to set it to private.
        """
        r = method_call.call_api(method = "flickr.photos.geo.setPerms", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)

    def setLicence(self,license):
        """ method: flickr.photos.licenses.setLicense
            Sets the license for a photo.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            license_id (Required)
                The license to apply, or 0 (zero) to remove the current 
                license. Note : as of this writing the "no known copyright
                restrictions" license (7) is not a valid argument. 
        """
        if isinstance(license,License):
            license_id = license.id
        else :
            license_id = license

        r = method_call.call_api(method = "flickr.photos.licenses.setLicense", photo_id = self.id, license_id = license_id , auth_handler = AUTH_HANDLER)         

    def setLocation(self,**args):
        """ method: flickr.photos.geo.setLocation
    
            Sets the geo data (latitude and longitude and, optionally, the 
            accuracy level) for a photo. Before users may assign location
            data to a photo they must define who, by default, may view that
            information. Users can edit this preference at 
            http://www.flickr.com/account/geo/privacy/. If a user has not 
            set this preference, the API method will return an error.
            
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            lat (Required)
                The latitude whose valid range is -90 to 90. Anything more 
                than 6 decimal places will be truncated.
            lon (Required)
                The longitude whose valid range is -180 to 180. Anything 
                more than 6 decimal places will be truncated.
            accuracy (Optional)
                Recorded accuracy level of the location information. World 
                level is 1, Country is ~3, Region ~6, City ~11, Street ~16. 
                Current range is 1-16. Defaults to 16 if not specified.
            context (Optional)
                Context is a numeric value representing the photo's 
                geotagginess beyond latitude and longitude. For example, 
                you may wish to indicate that a photo was taken "indoors" 
                or "outdoors".

                The current list of context IDs is :

                    * 0, not defined.
                    * 1, indoors.
                    * 2, outdoors.

                The default context for geotagged photos is 0, or "not defined" 
                    
        """
        r = method_call.call_api(method = "flickr.photos.geo.setLocation", photo_id = self.id, auth_handler = AUTH_HANDLER,**args)
        

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

class PhotoPerson(Person):
    __converters__ = [
        dict_converter(["x","y","h","w"],int)
    ]
    __display__ = ["id","photo","username","x","y","h","w"]
    
    def delete(self):
        """ method: flickr.photos.people.delete
            Remove a person from a photo.
            
        Authentication:
            This method requires authentication with 'write' permission.
            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.photos.people.delete", user_id = self.id, photo_id = self.photo.id,auth_handler = AUTH_HANDLER)
        return r
    
    def deleteCoords(self):
        """ method: flickr.photos.people.deleteCoords
            Remove the bounding box from a person in a photo
            
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.photos.people.deleteCoords", user_id = self.id, photo_id = self.photo.id,auth_handler = AUTH_HANDLER)
        return r

    def editCoords(self,**args):
        """ method: flickr.photos.people.editCoords
            Edit the bounding box of an existing person on a photo.
            
        Authentication:
            This method requires authentication with 'write' permission.
            Note: This method requires an HTTP POST request.
        
        Arguments:
            person_x (Required)
                The left-most pixel co-ordinate of the box around the person.
            person_y (Required)
                The top-most pixel co-ordinate of the box around the person.
            person_w (Required)
                The width (in pixels) of the box around the person.
            person_h (Required)
                The height (in pixels) of the box around the person. 
        """
        r = method_call.call_api(method = "flickr.photos.people.deleteCoords", user_id = self.id, photo_id = self.photo.id,auth_handler = AUTH_HANDLER,**args)
        return r

class PhotoComment(FlickrObject):
    def delete(self):
        """ method: flickr.photos.comments.deleteComment
            Delete a comment as the currently authenticated user.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.test.login",comment_id = self.id, auth_handler = AUTH_HANDLER)

    def edit(self, comment_text):
        """ method: flickr.photos.comments.editComment
            Edit the text of a comment as the currently authenticated user.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            comment_text (Required)
                Update the comment to this text.
        """
        r = method_call.call_api(method = "flickr.test.login",comment_id = self.id, comment_text = comment_text, auth_handler = AUTH_HANDLER)

    @staticmethod
    def getRecentForContacts(**args):
        """ method: flickr.photos.comments.getRecentForContacts
        
            Return the list of photos belonging to your contacts that have been commented on recently.
        
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            date_lastcomment (Optional)
                Limits the resultset to photos that have been commented on since this date. The date should be in the form of a Unix timestamp.

                The default, and maximum, offset is (1) hour. 
            contacts_filter (Optional)
                A comma-separated list of contact NSIDs to limit the scope of the query to.
            extras (Optional)
                A comma-delimited list of extra information to fetch for each returned record. Currently supported fields are: description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_m, url_z, url_l, url_o
            per_page (Optional)
                Number of photos to return per page. If this argument is omitted, it defaults to 100. The maximum allowed value is 500.
            page (Optional)
                The page of results to return. If this argument is omitted, it defaults to 1. 
        """
        r = method_call.call_api(method = "flickr.test.login", auth_handler = AUTH_HANDLER,**args)
        return _extract_photo_list(r)
        
class PhotoGeo(object):
    @staticmethod
    def photosForLocation(**args):
        """ method:  flickr.photos.geo.photosForLocation
        
            Return a list of photos for the calling user at a specific 
            latitude, longitude and accuracy
        
        Authentication:
            This method requires authentication with 'read' permission.
        
        Arguments:
            lat (Required)
                The latitude whose valid range is -90 to 90. Anything more 
                than 6 decimal places will be truncated.
            lon (Required)
                The longitude whose valid range is -180 to 180. Anything 
                more than 6 decimal places will be truncated.
            accuracy (Optional)
                Recorded accuracy level of the location information. World 
                level is 1, Country is ~3, Region ~6, City ~11, Street ~16. 
                Current range is 1-16. Defaults to 16 if not specified.
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
        r = method_call.call_api(method = "flickr.photos.licences.getInfo",auth_handler = AUTH_HANDLER,**args)
        return _extract_photo_list(r)

class PhotoGeoPerms(FlickrObject):
    __converters__ = [
        dict_converter(["ispublic","iscontact","isfamily","isfriend"],bool)
    ]
    __display__ = ["id","ispublic","iscontact","isfamily","isfriend"]

class PhotoSet(FlickrObject):
    __converters__ = [
        dict_converter(["photos"],int),
    ]
    __display__ = ["id","title"]

    def addPhoto(self,**args):
        """ method: flickr.photosets.addPhoto

            Add a photo to the end of an existing photoset.

        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        Arguments:
            photo (Required)        
        """
        try :
            args["photo_id"] = args.pop("photo").id
        except KeyError : pass

        r = method_call.call_api(method = "flickr.photosets.add",photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)

    def addComment(self,**args):
        """ method: flickr.photosets.comments.addComment
        
            Add a comment to a photoset.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            comment_text (Required)
                Text of the comment 
        """
        r = method_call.call_api(method = "flickr.photosets.comments.addComment",photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)
        return PhotoSetComment(photoset = self,**r)

    @staticmethod
    def create(**args):
        """ method: flickr.photosets.create
            Create a new photoset for the calling user.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            title (Required)
                A title for the photoset.
            description (Optional)
                A description of the photoset. May contain limited html.
            primary_photo or primary_photo_id (Required)
                The photo or id of the photo to represent this set. The photo must belong to the calling user. 
        """
        try :
            pphoto = args.pop("primary_photo")
            if isinstance(pphoto,Photo):
                pphoto = pphoto.id
            pphoto["primary_photo_id"] = pphoto
        except KeyError: pass
    
        r = method_call.call_api(method = "flickr.photosets.create", auth_handler = AUTH_HANDLER,**args)
        photoset = r["photoset"]
        photoset["primary"] = Photo(id = photoset.pop("primary_photo_id"))
        return PhotoSet(**photoset)

    def delete(self):
        """ method: flickr.photosets.delete
            Delete a photoset.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.photosets.delete", photoset_id = self.id, auth_handler = AUTH_HANDLER)

    
    def editMeta(self,**args):
        """ method: flickr.photosets.editMeta
                Modify the meta-data for a photoset.
            
            Authentication:

                This method requires authentication with 'write' permission.

                Note: This method requires an HTTP POST request.
            
            Arguments:
                title (Required)
                    The new title for the photoset.
                description (Optional)
                    A description of the photoset. May contain limited html. 
            
        """
        r = method_call.call_api(method = "flickr.photosets.editMeta", photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)
    
    def editPhotos(self,**args):
        """ method:flickr.photosets.editPhotos

            Modify the photos in a photoset. Use this method to add, 
            remove and re-order photos.
            
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            primary_photo_id (Required)
                The id of the photo to use as the 'primary' photo for the 
                set. This id must also be passed along in photo_ids list 
                argument.
            photo_ids (Required)
                A comma-delimited list of photo ids to include in the set. 
                They will appear in the set in the order sent. This list 
                must contain the primary photo id. All photos must belong 
                to the owner of the set. This list of photos replaces the 
                existing list. Call flickr.photosets.addPhoto to append 
                a photo to a set.
        """
        
        try :
            args["primary_photo_id"] = args.pop("primary_photo").id
        except KeyError : pass
        try :
            args["photo_ids"] = [ p.id for p in args["photos"] ]
        except KeyError : pass
        
        photo_ids = args["photo_ids"]
        if isinstance(photo_ids,list):
            args["photo_ids"] = ", ".join(photo_ids)
            
        r = method_call.call_api(method = "flickr.photosets.editPhotos", photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)

    def getCommentList(self):
        """ method: flickr.photosets.comments.getList
            Returns the comments for a photoset.
        
        Authentication:

            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photosets.comments.getList", photoset_id = self.id)
        
        comments = r["comments"]["comment"]
        comments_ = []
        if not isinstance(comments,list):
            comments = [comments]
        for c in comments :
            author = c["author"]
            authorname = c.pop("authorname")
            c["author"] = Person(id = author,username = authorname)
            comments_.append(PhotoSetComment(photo = self,**c))
        return comments_

    def getContext(self,**args):
        """ method: flickr.photosets.getContext
        
            Returns next and previous photos for a photo in a set.
        
        Authentication:

            This method does not require authentication.
        
        Arguments:
            photo_id (Required)
                The id of the photo to fetch the context for.

        """
        
        try :
            photo_id = args.pop("photo").id
        except KeyError :
            photo_id = args["photo_id"]
        
        r = method_call.call_api(method = "flickr.photosets.getContext", photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)
        return Photo(**r["prevphoto"]),Photo(**r["nextphoto"])

    def getInfo(self):
        """ method: flickr.photosets.getInfo
        
            Gets information about a photoset.
            
        Authentication:
            This method does not require authentication.
        """
        r = method_call.call_api(method = "flickr.photosets.getInfo",photoset_id = self.id)
        photoset = r["photoset"]
        photoset["owner"] = Person(id = photoset["owner"])
        return photoset

    
    def getList(self,**args):
        """ method: flickr.photosets.getList
            Returns the photosets belonging to the specified user.
        
        Authentication:

            This method does not require authentication.
        
        Arguments:
            user_id (Optional)
                The NSID of the user to get a photoset list for. If none is specified, the calling user is assumed. 
        """
        
        try :
            args["user_id"] = args.pop("user").id
        except KeyError : pass
        
        r = method_call.call_api(method = "flickr.photosets.getList",**args)
        info = r["photosets"]
        photosets = info.pop("photoset")
        if not isinstance(photosets,list): phototsets = [photosets]
        return [ PhotoSet(**p) for ps in photosets ],Info(**info)

    def getPhotos(self,**args):
        """ method: flickr.photosets.getPhotos
            Get the list of photos in a set.
        
        Authentication:

            This method does not require authentication.
        
        Arguments:
            extras (Optional)
                A comma-delimited list of extra information to fetch for 
                each returned record. Currently supported fields are: license, 
                date_upload, date_taken, owner_name, icon_server, original_format, 
                last_update, geo, tags, machine_tags, o_dims, views, media, 
                path_alias, url_sq, url_t, url_s, url_m, url_o
            privacy_filter (Optional)
                Return photos only matching a certain privacy level. This 
                only applies when making an authenticated call to view a 
                photoset you own. Valid values are:

                    * 1 public photos
                    * 2 private photos visible to friends
                    * 3 private photos visible to family
                    * 4 private photos visible to friends & family
                    * 5 completely private photos

            per_page (Optional)
                Number of photos to return per page. If this argument is 
                omitted, it defaults to 500. The maximum allowed value is 500.
            page (Optional)
                The page of results to return. If this argument is omitted, 
                it defaults to 1.
            media (Optional)
                Filter results by media type. Possible values are all (default), 
                photos or videos 
        """
        
        try :
            extras = args["extras"]
            if isinstance(extras,list):
                args["extras"] = u",".join(extras)
        except KeyError : pass
        
        r = method_call.call_api(method = "flickr.photosets.getPhotos",photoset_id = self.id, **args)
        return _extract_photo_list(r)

    @staticmethod
    def orderSets(**args):
        """ method:flickr.photosets.orderSets
            Set the order of photosets for the calling user.
        
        Authentication:
            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            photoset_ids (Required)
                A comma delimited list of photoset IDs, ordered with the set to show
                first, first in the list. Any set IDs not given in the list will be 
                set to appear at the end of the list, ordered by their IDs. 
        
        """
        try :
            photosets = args.pop("photosets")
            args["photoset_ids"] = [ ps.id for ps in photosets ]
        except KeyError : pass
        
        photoset_ids = arsg["photoset_ids"]
        if isinstance(photoset_ids,list):
            args["photoset_ids"] = ", ".join(photoset_ids)
        
        r = method_call.call_api(method = "flickr.photosets.orderSets", auth_handler = AUTH_HANDLER,**args)
        
    def removePhoto(self,**args):
        """ method: flickr.photosets.removePhoto
            Remove a photo from a photoset.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            photo_id (Required)
                The id of the photo to remove from the set. 
        
        """
        
        try :
            args["photo_id"] = args.pop("photo").id
        except KeyError : pass
        
        r = method_call.call_api(method = "flickr.photosets.removePhoto", photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)
        
    def removePhotos(self,**args):
        """ method: flickr.photosets.removePhotos
            Remove multiple photos from a photoset.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            photo_ids (Required)
                Comma-delimited list of photo ids to remove from the photoset.
        """
        
        try :
            args["photo_ids"] = [ p.id for p in args.pop("photos") ]
        except KeyError : pass
        
        photo_ids = args["photo_ids"]
        if isinstance(photo_ids,list):
            args["photo_ids"] = u",".join(photo_ids)
        
        r = method_call.call_api(method = "flickr.photosets.removePhotos", photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)
    
    def reorderPhotos(self,**args):
        """ method: flickr.photosets.reorderPhotos
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            photo_ids (Required)
                Ordered, comma-delimited list of photo ids. Photos that are not in the list will keep their original order 
        """

        try :
            args["photo_ids"] = [ p.id for p in args.pop("photos") ]
        except KeyError : pass
        
        photo_ids = args["photo_ids"]
        if isinstance(photo_ids,list):
            args["photo_ids"] = u",".join(photo_ids)
        
        r = method_call.call_api(method = "flickr.photosets.reorderPhotos", photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)
       
    def setPrimaryPhoto(self,**args):
        """ method: flickr.photosets.setPrimaryPhoto
            Set photoset primary photo
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            photo_id (Required)
                The id of the photo to set as primary. 
        """
        try :
            args["photo_id"] = args.pop("photo").id
        except KeyError : pass
        
        r = method_call.call_api(method = "flickr.photosets.setPrimaryPhoto", photoset_id = self.id, auth_handler = AUTH_HANDLER,**args)

class PhotoSetComment(FlickrObject):
    def delete(self):
        """ method: flickr.photosets.comments.deleteComment
            Delete a photoset comment as the currently authenticated user.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        """
        r = method_call.call_api(method = "flickr.photosets.comments.deleteComment", comment_id = self.id, auth_handler = AUTH_HANDLER)

    def edit(self,**args):
        """ method: flickr.photosets.comments.editComment
            Edit the text of a comment as the currently authenticated user.
        
        Authentication:

            This method requires authentication with 'write' permission.

            Note: This method requires an HTTP POST request.
        
        Arguments:
            comment_text (Required)
                Update the comment to this text. 
        
        """
        r = method_call.call_api(method = "flickr.photosets.comments.editComment", comment_id = self.id, auth_handler = AUTH_HANDLER,**args)
        self._set_properties(**args)
        
        
class Pool(FlickrObject):
    pass

class Test(object):
    @staticmethod
    def login():
        r = method_call.call_api(method = "flickr.test.login",auth_handler = AUTH_HANDLER)
        return Person(**r["user"])

class UploadTicket(FlickrObject):
    pass

def _extract_photo_list(r):
    photos = []
    infos = r["photos"]
    pp = infos.pop("photo")
    if not isinstance(pp,list):
        pp = [pp]
    for p in pp :
        owner = Person(id = p["owner"])
        p["owner"] = owner
        photos.append( Photo(**p))
    return photos,Info(**infos)

def _check_list(obj):
    if isinstance(obj,list):
        return obj
    else :
        return [obj]




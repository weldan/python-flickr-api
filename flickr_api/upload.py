import method_call
from objects import Photo,UploadTicket

UPLOAD_URL = "http://api.flickr.com/services/upload/"
REPLACE_URL = "http://api.flickr.com/services/replace/"

AUTH_HANDLER = None



def upload(**args):
    """
    Authentication:

        This method requires authentication with 'write' permission.
        
    Arguments:
        photo_file
            The file to upload.
        title (optional)
            The title of the photo.
        description (optional)
            A description of the photo. May contain some limited HTML.
        tags (optional)
            A space-seperated list of tags to apply to the photo.
        is_public, is_friend, is_family (optional)
            Set to 0 for no, 1 for yes. Specifies who can view the photo.
        safety_level (optional)
            Set to 1 for Safe, 2 for Moderate, or 3 for Restricted.
        content_type (optional)
            Set to 1 for Photo, 2 for Screenshot, or 3 for Other.
        hidden (optional)
            Set to 1 to keep the photo in global search results, 2 to hide 
            from public searches.
        async
            set to 1 for async mode, 0 for sync mode 
    
    """
    if "async" not in args : args["async"] = True
    
    with open(args.pop("photo_file")) as p :
        args["photo"] = p.read()

    r = method_call.call_api(auth_handler = AUTH_HANDLER,exclude_signature = ["photo"],url = UPLOAD_URL, **args)
    if async :
        return UploadTicket(id = r["ticketid"])
    else :
        return r

    
def replace(**args):
    """
     Authentication:

        This method requires authentication with 'write' permission.

        For details of how to obtain authentication tokens and how to sign 
        calls, see the authentication api spec. Note that the 'photo' parameter 
        should not be included in the signature. All other POST parameters 
        should be included when generating the signature.
    
    Arguments:

        photo_file
            The file to upload.
        photo_id
            The ID of the photo to replace.
        async (optional)
            Photos may be replaced in async mode, for applications that 
            don't want to wait around for an upload to complete, leaving 
            a socket connection open the whole time. Processing photos 
            asynchronously is recommended. Please consult the documentation 
            for details. 
            
    """
    if "async" not in args : args["async"] = True
    if "photo" in args : args["photo_id"] = args.pop("photo").id
    with open(args.pop("photo_file")) as p :
        args["photo"] = p.read()
        
    r = method_call.call_api(auth_handler = AUTH_HANDLER,exclude_signature = ["photo"],url = UPLOAD_URL, **args)
    if async :
        return UploadTicket(id = r["ticketid"])
    else :
        return r

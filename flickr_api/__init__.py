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

from objects import *
import objects
from auth import AuthHandler
import upload

def set_auth_handler(auth_handler):
    objects.AUTH_HANDLER = auth_handler
    upload.AUTH_HANDLER = auth_handler

import flickr_api
from flickr_api.method_call import clean_content


flickr_api.set_auth_handler(flickr_api.AuthHandler.load("access.dat"))

u = flickr_api.Person.findByUserName("AlexM14")
u.load()

print u

p,info = u.getPublicPhotos()
print u.getPublicPhotos()
print u.getPhotosOf(u)
print u.getPublicGroups()
print flickr_api.Collection.getTree()

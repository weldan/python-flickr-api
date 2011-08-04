import flickr_api



flickr_api.set_auth_handler(flickr_api.AuthHandler.load("access.dat"))

#~ 
u = flickr_api.Person.findByUserName("AlexM14")
p = u.getPublicPhotos()
print str(p)
print u.getPhotosOf(u)
print u.getPublicGroups()

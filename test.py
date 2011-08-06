import flickr_api
from flickr_api.method_call import clean_content


flickr_api.set_auth_handler(flickr_api.AuthHandler.load("access.dat"))



d = { 't' : { '_content' : 0 },
      'p' : { '_content' : 1 ,
              'q' : 2 ,
              'r' : { '_content' : 3}
              },
    }
print clean_content(d)
              

u = flickr_api.Person.findByUserName("AlexM14")
u.load()

print flickr_api.Prefs.getHidden()

#~ p,info = u.getPublicPhotos()
#~ print u.getPublicPhotos()
#~ print u.getPhotosOf(u)
#~ print u.getPublicGroups()
#~ print flickr_api.Collection.getTree()
print flickr_api.CommonInstitution.getInstitutions()

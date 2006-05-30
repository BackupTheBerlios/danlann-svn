"""
Danlann data model. Module contain definitions of gallery, album and photo
classes.
"""

import os.path

class Element(object):
    """
    Basic class for all gallery business classes. This class contains title
    and description attributes.

    @ivar title:       item title
    @ivar description: item description
    """
    def __init__(self):
        self.title       = None
        self.description = None



class Item(Element):
    """
    Basic class for albums and photos.

    @ivar gallery:     gallery reference
    @ivar album:       parent album, can be @C{None}
    """
    def __init__(self):
        super(Item, self).__init__()
        self.gallery     = None
        self.album       = None



class Photo(Item):
    """
    Gallery photo.

    @ivar file: filename of photo, no extension, no directory
    """
    def __init__(self):
        super(Photo, self).__init__()
        self.file = None
        self.exif = []



class Album(Item):
    """
    Gallery album.

    @ivar subalbums: albums included in this album
    @ivar photos:    album photos
    @ivar thumbnail: album thumbnail
    @ivar dir:       album directory counted from gallery root
    """
    def __init__(self):
        super(Album, self).__init__()
        self.dir = None
        self.thumbnail = None
        self.subalbums = [] 
        self.photos = [] 


    def isFirstPhoto(self, item): # fixme:
        return self.photos[0] == item


    def isLastPhoto(self, item):  # fixme: do we need it?
        return self.photos[-1] == item



class Gallery(Element):
    """
    Gallery representation.

    @ivar subalbums: gallery root albums
    """
    def __init__(self):
        super(Gallery, self).__init__()
        self.subalbums = []


    def reldir(self, dir):
        return os.path.basename(dir)


    def rootdir(self, album):
        dirs = album.dir.split('/')
        return '/'.join(('..', ) * len(dirs))


__all__ = [Gallery, Album, Photo]

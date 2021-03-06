#
# Danlann - Memory Jail - an easy to use photo gallery generator.
#
# Copyright (C) 2006 by Artur Wroblewski <wrobell@pld-linux.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#

"""
Danlann gallery data model. Module contain definitions of gallery, album
and photo classes.
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
        self.title       = ''
        self.description = ''



class Item(Element):
    """
    Basic class for albums and photos.

    @ivar gallery:     gallery reference
    """
    def __init__(self):
        super(Item, self).__init__()
        self.gallery     = None



class Photo(Item):
    """
    Gallery photo.

    @ivar name    : filename of photo, no extension, no directory
    @ivar filename: absolute path to a photo 
    """
    def __init__(self):
        super(Photo, self).__init__()
        self.name     = None
        self.filename = None
        self.exif     = []



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

    @ivar title:       gallery title
    @ivar description: gallery description
    @ivar subalbums:   gallery root albums
    """
    def __init__(self, title, description):
        super(Gallery, self).__init__()
        self.subalbums = []
        self.title = title
        self.description = description


    def reldir(self, dir):
        return os.path.basename(dir)


    def rootdir(self, album):
        dirs = album.dir.split('/')
        return '/'.join(('..', ) * len(dirs))


__all__ = [Gallery, Album, Photo]

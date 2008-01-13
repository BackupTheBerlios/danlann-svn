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

import stringtemplate

from danlann.bc import Gallery, Album, Photo
import danlann.config

class Template(object):
    """
    A template.

    @ivar gallery: gallery reference
    @ivar st_group: StringTemplate reference
    """
    def __init__(self, gallery):
        """
        Create new instance of a template with gallery instance reference.
        """
        super(Template, self).__init__()
        self.gallery = gallery
        self.st_group = stringtemplate.StringTemplateGroup('basic',
                '%s/tmpl' % danlann.config.libpath)
        self.st_group.registerRenderer(str, XMLRenderer());
        self.st_group.registerRenderer(unicode, XMLRenderer());

        self.tmpl_gallery = 'basic/gallery'
        self.tmpl_page = 'basic/page'
        self.tmpl_album = 'basic/album'
        self.tmpl_photo = 'basic/photo'
        self.tmpl_exif = 'basic/exif'


    def getPage(self, tmpl, rootdir, cls):
        """
        Get page template for gallery page, album page or photo page. 

        @param tmpl: page template name
        @param rootdir: relative path to gallery directory
        @param cls: page class
        """
        page = self.st_group.getInstanceOf(self.tmpl_page)

        page['gallery'] = self.gallery
        page['class'] = cls
        page['tmpl'] = tmpl
        page['rootdir'] = rootdir

        return page


    def write(self, f, page):
        """
        Write page template to file.

        @param f: page output file
        @param page: page to be saved
        """
        print >> f, str(page)


    def galleryPage(self, f):
        """
        Generate gallery page.
        """
        # rootdir is current directory
        page = self.getPage(self.tmpl_gallery, '.', 'gallery')
        self.write(f, page)


    def albumPage(self, f, album, parent):
        """
        Generate album page.
        """
        rootdir = self.gallery.rootdir(album)

        page = self.getPage(self.tmpl_album, rootdir, 'album')
        page['parent'] = parent
        page['album'] = album
        page['prev'] = parent.prev(album)
        page['next'] = parent.next(album)

        self.write(f, page)


    def photoPage(self, f, photo):
        """
        Generate photo page.
        """
        album = photo.album
        rootdir = self.gallery.rootdir(photo.album)

        page = self.getPage(self.tmpl_photo, rootdir, 'photo preview')
        page['photo'] = photo
        page['album'] = album
        page['prev'] = album.prev(photo)
        page['next'] = album.next(photo)

        self.write(f, page)


    def exifPage(self, f, photo):
        """
        Generate photo exif page.
        """
        album = photo.album
        rootdir = self.gallery.rootdir(photo.album)

        page = self.getPage(self.tmpl_exif, rootdir, 'photo exif')
        page['photo'] = photo
        page['album'] = album
        page['prev'] = album.prev(photo)
        page['next'] = album.next(photo)

        self.write(f, page)



class XMLRenderer(stringtemplate.AttributeRenderer):
    """
    XML renderer for StringTemplate library to convert special characters
    into XML entities.
    """
    def str(self, val):
        assert val is not None
        val = val.replace('&', '&amp;')
        val = val.replace('\'', '&apos;')
        val = val.replace('"', '&quot;')
        val = val.replace('<', '&lt;')
        val = val.replace('>', '&gt;')
        return val

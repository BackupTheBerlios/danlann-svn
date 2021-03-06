#
# Danlann - Memory Jail - an easy to use photo gallery generator.
#
# Copyright (C) 2006-2008 by Artur Wroblewski <wrobell@pld-linux.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re

import stringtemplate

from danlann.bc import Gallery, Album, Photo
import danlann.config

class Template(object):
    """
    A template.

    @ivar gallery: gallery reference
    @ivar copyright: copyright text
    @ivar st_group: StringTemplate reference
    @ivar css: list of css files
    @ivar js: list of javascript files
    """
    def __init__(self, name, gallery, override=None):
        """
        Create new instance of a template with gallery instance reference.

        @param name: template name
        @param gallery: gallery reference
        @param override: directory overriding template 
        """
        super(Template, self).__init__()
        self.name = name
        self.gallery = gallery

        self.css = ['css/danlann.css']
        self.js = ['js/jquery.js', 'js/danlann.js']
        self.copyright = None

        st_group = stringtemplate.StringTemplateGroup('basic',
                '%s/tmpl' % danlann.config.libpath)
        st_group.registerRenderer(str, XMLRenderer());
        st_group.registerRenderer(unicode, XMLRenderer());

        # set template override if defined
        # template override is realized with StringTemplate
        # supergroup/subgroup functionality
        if override:
            self.st_group = stringtemplate.StringTemplateGroup(name, override)
            self.st_group.registerRenderer(str, XMLRenderer());
            self.st_group.registerRenderer(unicode, XMLRenderer());

            self.st_group.setSuperGroup(st_group)
        else:
            self.st_group = st_group # no override

        self.tmpl_gallery = '%s/gallery' % self.name
        self.tmpl_page    = '%s/page' % self.name
        self.tmpl_album   = '%s/album' % self.name
        self.tmpl_photo   = '%s/photo' % self.name
        self.tmpl_exif    = '%s/exif' % self.name


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
        page['copyright'] = self.copyright
        page['css'] = self.css
        page['js'] = self.js

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

        page = self.getPage(self.tmpl_photo, rootdir, 'photo')
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

        page = self.getPage(self.tmpl_exif, rootdir, 'exif')
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
    def __init__(self, *args, **kw):
        super(XMLRenderer, self).__init__(*args, **kw)
        # url starts with http and ends with a printable character or slash
        # <> is not in a link
        self.link = re.compile(r'(\bhttps?://\w[^<>\s]+[\w/])')

    def str(self, val):
        assert val is not None
        val = val.replace('&', '&amp;')
        val = val.replace('\'', '&apos;')
        val = val.replace('"', '&quot;')
        val = val.replace('<', '&lt;')
        val = val.replace('>', '&gt;')

        # new line to <br/> tag
        val = val.replace('\\n', '<br/>')

        # support links
        val = self.link.sub('<a href = \'\\1\'>\\1</a>', val)

        return val

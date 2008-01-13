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
Test templating functionality.
"""

from ConfigParser import ConfigParser
from StringIO import StringIO
import stringtemplate
import unittest

from danlann import Danlann
from danlann.bc import Photo, Album, Exif

CONF = """
[danlann]
title     = danlann title test

albums    = a.txt b.txt
indir     = input_dir
outdir    = output_dir
"""

class TemplateVariablesTestCase(unittest.TestCase):
    """
    Test if template variables are provided by templating functionality.
    """
    def setUp(self):
        """
        Prepare configuration data and initialize Danlann processor
        for a test case.
        """
        self.conf = ConfigParser()
        conf = ConfigParser()
        conf.readfp(StringIO(CONF))
        assert not conf.has_option('danlann', 'validate')

        # initialize processor
        self.processor = Danlann()
        self.processor.initialize(conf, False)
        self.generator = self.processor.generator
        self.filemanager = self.processor.fm

        tmpl = self.tmpl = self.generator.tmpl
        tmpl.tmpl_page = 'page'
        tmpl.tmpl_album = 'album'


    def _setTemplate(self, tmpl):
        self.tmpl.st_group = stringtemplate.StringTemplateGroup(StringIO(tmpl))


    def testGalleryPageVairables(self):
        """gallery page template variables"""
        self._setTemplate("""\
group basic;
page(gallery, class, tmpl, rootdir) ::= "'$gallery.title$' $class$ $tmpl$ $rootdir$"
""")

        f = StringIO()
        self.tmpl.galleryPage(f)
        self.assertEquals('\'danlann title test\' gallery basic/gallery .\n', f.getvalue())


    def testAlbumPageVairables(self):
        """album page template variables"""
        self._setTemplate("group basic;\n" \
                "page(gallery, class, tmpl, rootdir, album," \
                "           parent, prev, next) ::=" \
                " \"'$gallery.title$' $class$ $tmpl$ $rootdir$" \
                " p:$prev.title$ n:$next.title$ $parent.title$\"")

        f = StringIO()
        a1 = Album()
        a1.title = 'a 1 title'
        a1.dir = 'a/b/c'
        a2 = Album()
        a2.title = 'a 2 title'
        a2.dir = 'a/b/d'
        parent = self.tmpl.gallery
        parent.subalbums.extend([a1, a2])

        self.tmpl.albumPage(f, a1, parent)

        expected = "'danlann title test' album album ../../.." \
                " p: n:a 2 title danlann title test\n"
        self.assertEquals(expected, f.getvalue())


    def testPhotoPageVariables(self):
        """photo page template variables"""
        self._setTemplate("group basic;\n" \
                "page(gallery, class, tmpl, rootdir, album," \
                "           photo, prev, next) ::=" \
                " \"'$gallery.title$' $class$ $tmpl$ $rootdir$" \
                " p:$prev.title$ n:$next.title$ $album.title$\"")

        f = StringIO()
        album = Album()
        album.title = 'a title'
        album.dir = 'a/b/c'
        parent = self.tmpl.gallery
        parent.subalbums.append(album)

        p1 = Photo()
        p1.title = 'p1'
        p1.name = 'n1'
        p1.album = album

        p2 = Photo()
        p2.title = 'p2'
        p2.name = 'n2'
        p2.album = album

        album.photos.extend([p1, p2])

        self.tmpl.photoPage(f, p1)

        expected = "'danlann title test' photo preview basic/photo ../../.. p: n:p2 a title\n"
        self.assertEquals(expected, f.getvalue())


    def testExifPageVariables(self):
        """exif page template variables"""
        self._setTemplate("group basic;\n" \
                "page(gallery, class, tmpl, rootdir, album," \
                "           photo, prev, next) ::=" \
                " \"'$gallery.title$' $class$ $tmpl$ $rootdir$" \
                " p:$prev.title$ n:$next.title$ $album.title$" \
                " $photo.exif: {e | n:$e.name$v:$e.value$}$\"")

        f = StringIO()
        album = Album()
        album.title = 'a title'
        album.dir = 'a/b/c'
        parent = self.tmpl.gallery
        parent.subalbums.append(album)

        p1 = Photo()
        p1.title = 'p1'
        p1.name = 'n1'
        p1.album = album

        p1.exif.append(Exif('ea', 'ev'))
        p1.exif.append(Exif('ez', 'eq'))

        p2 = Photo()
        p2.title = 'p2'
        p2.name = 'n2'
        p2.album = album

        album.photos.extend([p1, p2])

        self.tmpl.photoPage(f, p1)

        expected = "'danlann title test' photo preview basic/photo" \
                " ../../.. p: n:p2 a title n:eav:evn:ezv:eq\n"
        self.assertEquals(expected, f.getvalue())

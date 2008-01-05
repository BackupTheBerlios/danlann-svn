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

class Template(object):
    """
    A template.
    """
    def __init__(self, gallery):
        """
        Create new instance of a template with gallery instance reference.
        """
        super(Template, self).__init__()
        self.gallery = gallery
        self.st_group = stringtemplate.StringTemplateGroup('basic', '/home/users/wrobell/projects/danlann/danlann/trunk/tmpl')


    def getPage(self, body, rootdir, cls):
        page = self.st_group.getInstanceOf('basic/page')

        page['gallery'] = self.gallery
        page['class'] = cls
        page['body'] = str(body)
        page['rootdir'] = rootdir

        return str(page)

    def galleryIndex(self, f):
        body = self.st_group.getInstanceOf('basic/gallery')

        body['gallery'] = self.gallery
        print >> f, self.getPage(body, '.', 'gallery')


    def albumIndex(self, album, parent, f):
        rootdir = self.gallery.rootdir(album)
        body = self.st_group.getInstanceOf('basic/album')
        body['rootdir'] = rootdir
        body['gallery'] = self.gallery
        body['album'] = album
        body['parent'] = parent

        print >> f, self.getPage(body, rootdir, 'album')


    def photo(self, photo, f):
        rootdir = self.gallery.rootdir(photo.album)
        body = self.st_group.getInstanceOf('basic/photo')
        body['rootdir'] = rootdir
        body['gallery'] = self.gallery
        body['album'] = photo.album
        body['photo'] = photo

        print >> f, self.getPage(body, rootdir, 'photo preview')


def escape(self, val):
    if val is None:
        return val
    val = val.replace('&', '&amp;')
    val = val.replace('\'', '&apos;')
    val = val.replace('"', '&quot;')
    val = val.replace('<', '&lt;')
    val = val.replace('>', '&gt;')

    val = val.replace('\\n', '<br/>')
    return val



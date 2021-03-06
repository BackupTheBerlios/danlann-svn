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

from danlann.bc import Gallery, Album, Photo

class XHTMLTemplate(object):
    def __init__(self, conf):
        self.conf = conf

        self.copyright = ''

        self.css = ['css/danlann.css']
        if conf.has_option('template', 'css'):
            self.css += self.conf.get('template', 'css').split()

        if conf.has_option('template', 'copyright'):
            self.copyright = self.conf.get('template', 'copyright')

        self.js = ['js/danlann.js']
        if conf.has_option(self.__conf__, 'js'):
            self.js += conf.get(self.__conf__, 'js').split()

        self.onload = ''
        if conf.has_option(self.__conf__, 'onload'):
            self.onload = ' onload = \'%s\'' % conf.get(self.__conf__, 'onload')

        fmt = '<link rel = \'stylesheet\' href = \'%%s/%s\' type = \'text/css\'></link>'
        cssfiles = ''.join([fmt % f for f in self.css])

        fmt = '<script src = \'%%s/%s\' type = \'text/javascript\'></script>'
        jsfiles = ''.join([fmt % f for f in self.js])

        # params:
        # - XHTML header title
        # - 'gallery', 'album' or 'photo' used for body class
        self.header = '<!DOCTYPE html PUBLIC \'-//W3C//DTD XHTML 1.0 Strict//EN\' \'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\'>' \
                '<html xmlns=\'http://www.w3.org/1999/xhtml\'><head><title>%s</title>' \
            + cssfiles + jsfiles \
            + '</head><body class = \'%s\'' + self.onload + '><div id = \'body\' class = \'body\'>'
        self.footer = '<div class = \'footer\'>' \
            '<span class = \'danlann\'>' \
            '[ <a href = \'http://danlann.berlios.de\'>generated by danlann</a> ]' \
            ' [ <a href = \'http://openfacts.berlios.de/index-en.phtml?title=DanlannDisclaimer\'>' \
            'problem viewing this page? click here!</a> ]' \
            '</span>' \
            ' <span class = \'copyright\'>' + self.copyright + '</span>' \
            '</div>' \
            '</div>' \
            '</body></html>'


    #
    # helper methods
    #
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
    

    def photoTitle(self, photo):
        return self.escape('%s: %s' % (photo.album.title, photo.title))


    def fileTitle(self, context):
        if isinstance(context, Album):
            gallery = context.gallery
            title = '%s - %s' % (gallery.title, context.title)
        elif isinstance(context, Photo):
            album = context.album
            gallery = album.gallery
            title = '%s - %s - %s' % (gallery.title, album.title, context.title)
        else:
            title = context.title

        assert title

        return self.escape(title)


    def simpleTag(self, tag, cls, content = ''):
        data = {
            'tag': tag,
            'cls': cls,
            'content': self.escape(content),
        }
        pre = '<%(tag)s class = \'%(cls)s\'>%(content)s' % data
        post = '</%(tag)s>' % data
        return pre, post


    #
    # template interface methods
    #
    def body(self, context, photo_type = None):
        if isinstance(context, Album):
            body_cls = 'album'
            rootdir = context.gallery.rootdir(context)
        elif isinstance(context, Photo):
            body_cls = 'photo %s' % photo_type
            rootdir = context.gallery.rootdir(context.album)
        else:
            body_cls = 'gallery'
            rootdir = '.'

        rootdirs = list((rootdir, ) * (len(self.css) + len(self.js)))
        data = [self.fileTitle(context)] + rootdirs + [body_cls]
        header = self.header % tuple(data)

        footer = self.footer

        return header, footer


    def title(self, context, photo_type = None):
        if isinstance(context, Photo):
            title = '%s: %s' % (context.album.title, context.title)
        else:
            title = context.title
        return self.simpleTag('h1', 'title', title)


    def description(self, context, photo_type = None):
        return self.simpleTag('p', 'description', context.description)


    def albums(self, context, photo_type = None):
        return self.simpleTag('div', 'albums')


    def photos(self, context, photo_type = None):
        """
        Table is used instead of div because of crappy browser, which do
        not support CSS well.
        """

        self.column_counter = 1  # used to count columns in photos table

        pre, post = self.simpleTag('table', 'photos')
        return pre, post


    def navigation(self, context, data, photo_type = None):
        assert 'parent' in data
        assert 'parent_title' in data
        assert 'prev_title' in data
        assert 'prev_item' in data
        assert 'next_title' in data
        assert 'next_item' in data

        tmp = {}
        for k, v in data.items():
            tmp[k] = self.escape(v)
        data = tmp
        
        navigation = ['<div class = \'navigation\'>']

        if data['prev_item']:
            navigation.append('<a title = \'%(prev_title)s\' href = \'%(prev_item)s\'><span class = \'prev\'/></a>')
        else:
            navigation.append('<span class = \'prev disabled\'/>')

        navigation.append('<a title = \'%(parent_title)s\' href = \'%(parent)s\'><span class = \'parent\' /></a>')

        if data['next_item']:
            navigation.append('<a title = \'%(next_title)s\' href = \'%(next_item)s\'><span class = \'next\'/></a>')
        else:
            navigation.append('<span class = \'next disabled\'/>')

        if isinstance(context, Photo) and context.exif:
            navigation.append('<span class = \'exif\'>')
            navigation.append('<a onclick = \'toggle_exif_window("%s.exif.xhtml"); return false\'' % context.name)
            navigation.append(' title = \'exif data\' href = \'%s.exif.xhtml\'>exif</a></span>' % context.name)
        navigation.append('</div>')
        return ''.join(navigation) % data, ''


class XHTMLGalleryIndexTemplate(XHTMLTemplate):
    """
    XHTML Simple gallery template.
    """
    __conf__ = 'template:gallery'

    def album(self, album):
        title = self.escape(album.title)
        pre = '<div class = \'album\'><a title = \'%s\' href = \'%s/index.xhtml\'>%s</a>' \
            % ('album: %s' % title, album.dir, title)
        post = '</div>'
        return pre, post



class XHTMLAlbumIndexTemplate(XHTMLTemplate):
    __conf__ = 'template:album'

    def album(self, album):
        title = self.escape(album.title)
        return "<div class = 'album'><a title = \'%s\' href = '%s/index.xhtml'>%s</a></div>" \
            % ('album: %s' % title, album.gallery.reldir(album.dir), title), ''


    def photo(self, photo):
        data = {
            'url': photo.name,
            'title': self.escape(photo.title),
            'alt': 'photo: %s' % self.escape(photo.title),
        }

        row_pre = row_post = ''
        if self.column_counter % 5 == 1:
            row_pre = '<tr>'
        if self.column_counter % 5 == 0 or photo.album.photos[-1] == photo:
            row_post = '</tr>'    # close row every 5th photo or after last one photo
        self.column_counter += 1
        
        return (row_pre + '<td class = \'photo\'><a title = \'%(title)s\' href = \'%(url)s.preview.xhtml\'>' \
            '<img alt = \'%(alt)s\' src = \'%(url)s.thumb.jpg\'/></a><div>%(title)s</div>' \
            '</td>' + row_post) % data, ''


class XHTMLPhotoTemplate(XHTMLTemplate):
    __conf__ = 'template:photo'

    CTYPES = {
        'preview': 'view',
        'view': 'preview',
    }

    def photo(self, photo, photo_type):
        data = {
            'url': photo.name,
            'type': photo_type,
            'ctype': self.CTYPES[photo_type],
            'title': '%s' % self.escape(photo.title),
            'alt': 'photo: %s' % self.escape(photo.title),
        }

        return ('<div class = \'photo %(type)s\'>' \
                '<a title = \'%(title)s\' href = \'%(url)s.%(ctype)s.xhtml\'>' \
                '<img alt = \'%(alt)s\' src = \'%(url)s.%(type)s.jpg\'/>' \
                '</a></div>') % data, ''


    def photoExif(self, photo):
        body = ['<table>']
        body += ['<tr><th>%s</th><td>%s</td></tr>' % (self.escape(data[0]), self.escape(data[1])) for data in photo.exif]
        body.append('</table>')
        return ''.join(body)



class XHTMLExifTemplate(XHTMLPhotoTemplate):
    __conf__ = 'template:exif'

    def photo(self, photo, photo_type = None):
        return self.photoExif(photo), ''

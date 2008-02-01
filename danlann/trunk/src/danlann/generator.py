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

import sys
import os
import os.path

from danlann.bc import Gallery, Album, Photo

import logging
log = logging.getLogger('danlann.generator')



class ConversionArguments(list):
    """
    Photo conversion arguments list.

    Arguments list is used for photo conversion with ImageMagick
    or GraphicsMagick.

    @ivar size    : target photo size
    @ivar quality : photo image quality
    @ivar unsharp : sharpen parameters
    @ivar params  : additional conversion parameters
    """

    def __init__(self, size):
        """
        Create photo conversion arguments list.

        @param size: target photo size
        """
        super(ConversionArguments, self).__init__()
        self.__dict__['size']    = size
        self.__dict__['quality'] = '90'
        self.__dict__['unsharp'] = '0.1x0.1+2.0+0'
        self.__dict__['params']  = []

        self.rebuild()


    def __setattr__(self, name, value):
        """
        Set conversion arguments parameters.

        List of arguments is rebuilt.

        @param name  : argument name
        @param value : argument value
        """
        if not hasattr(self, name):
            raise AttributeError('unsupported photo conversion option "%s"' % name)

        if name == 'params':
            value = value.split()

        self.__dict__[name] = value
        self.rebuild()


    def rebuild(self):
        """
        Rebuild conversion argument list.
        """
        del self[:]
        self.append('-resize')
        self.append(self.size)

        if self.quality:
            self.append('-quality')
            self.append(self.quality)

        self += self.params

        if self.unsharp:
            self.append('-unsharp')
            self.append(self.unsharp)



class DanlannGenerator(object):
    """
    Gallery generator.

    @ivar indir        : gallery input directories
    @ivar outdir       : gallery output dir
    @ivar convert_args : photo conversion parameters
    @ivar fm           : file manager

    @ivar tmpl         : gallery template
    """
    def __init__(self, gallery, fm):
        self.indir        = []
        self.outdir       = None
        self.gallery      = gallery
        self.fm           = fm
        self.exif_headers = []

        self.convert_args = {
            'thumb'   : ConversionArguments('128x128>'),
            'image' : ConversionArguments('800x600>'),
        }

        self.tmpl = None
        self.etmpl = None


    def setConvertArg(self, photo_type, opt, value):
        """
        Set conversion argument for given photo type.

        @param photo_type : photo type
        @param opt        : conversion argument name
        @param value      : conversion argument value
        """
        setattr(self.convert_args[photo_type], opt, value)


    def getDir(self, album):
        return os.path.normpath('%s/%s' % (self.outdir, album.dir))


    def getAlbumFile(self, album, file):
        return '%s/%s' % (self.getDir(album), file)
        

    def getPhotoFile(self, photo, photo_type, ext = 'xhtml'):
        """
        Return photo filename for given type of photo.

        For example for dsc_0000 thumbnail we return

            dsc_0000.thumb.xhtml
        """
        if photo_type is None:
            return '%s.%s' % (photo.name, ext)
        else:
            return '%s.%s.%s' % (photo.name, photo_type, ext)


    def generate(self):
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        f = open('%s/index.xhtml' % self.outdir, 'w')
        self.tmpl.galleryPage(f)
        f.close()

        for album in self.gallery.subalbums:
            self.generateAlbum(album, self.gallery)

        log.info('generated index page')


    def generateAlbum(self, album, parent):
        self.fm.mkdir(self.getDir(album))
        fn = self.getAlbumFile(album, 'index.xhtml')

        f = open(fn, 'w')
        self.tmpl.albumPage(f, album, parent)
        f.close()

        for subalbum in album.subalbums:
            self.generateAlbum(subalbum, album)

        for photo in album.photos:
            self.generateAlbumPhotos(photo)

        log.info('generated album %s' % album.dir)


    def generateAlbumPhotos(self, photo):
        try:
            # lookup photo input absolute filename
            files = self.fm.lookup(self.indir, '%s.jpg' % photo.name)
            photo.filename = files.next()

            self.generateExif(photo)
            self.convertPhoto(photo, 'thumb')
            self.convertPhoto(photo)

            self.generatePhoto(photo)
        except StopIteration, ex:
            log.error('could not find photo %s file' % photo.name)


    def generateExif(self, photo):
        photo.exif = self.fm.getExif(photo.filename, self.exif_headers)

        if photo.exif:
            exif_fn = self.getPhotoFile(photo, 'exif')
            f = open(self.getAlbumFile(photo.album, exif_fn), 'w')
            self.tmpl.exifPage(f, photo)
            f.close()
            log.info('generated exif page for photo %s' % photo.name)
        else:
            log.error('photo %s does not contain exif' % photo.name)



    def convertPhoto(self, photo, photo_type=None):
        fn_in  = None
        fn_out = '%s/%s/%s' % (self.outdir,
            photo.album.dir,
            self.getPhotoFile(photo, photo_type, 'jpg'))

        if os.path.exists(fn_out):
            log.info('leaving intact %s' % fn_out)
        elif photo.filename:
            log.info('converting to %s' % fn_out)
            try :
                # get conversion parameters
                pt = 'image'
                if photo_type is not None:
                    pt = photo_type
                assert pt in self.convert_args
                args = self.convert_args[pt]

                self.fm.convert(photo.filename, fn_out, args)
            except OSError, ex:
                log.error('failed conversion %s: %s' % (fn_out, ex))


    def generatePhoto(self, photo, photo_type=None):
        """
        Generate photo page.
        """
        fn = self.getAlbumFile(photo.album,
            self.getPhotoFile(photo, photo_type))

        f = open(fn, 'w')
        self.tmpl.photoPage(f, photo)
        f.close()

        log.info('generated photo page %s.%s' % (photo.name, photo_type))


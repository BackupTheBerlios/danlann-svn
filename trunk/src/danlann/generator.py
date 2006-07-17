import sys
import os
import os.path

from danlann.bc import Gallery, Album, Photo
from danlann.filemanager import File

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
        self.__dict__['unsharp'] = '3x3+0.5+0'
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

    @ivar gtmpl        : gallery template
    @ivar atmpl        : album template
    @ivar ptmpl        : photo template
    """
    def __init__(self, gallery, fm):
        self.indir        = []
        self.outdir       = None
        self.gallery      = gallery
        self.fm           = fm
        self.exif_headers = []

        self.convert_args = {
            'thumb'   : ConversionArguments('128x128>'),
            'preview' : ConversionArguments('800x600>'),
            'view'    : ConversionArguments('1024x768>'),
        }

        self.gtmpl = None
        self.atmpl = None
        self.ptmpl = None
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


    def getFile(self, album, file):
        return '%s/%s' % (self.getDir(album), file)
        

    def getPhotoFile(self, photo, photo_type, ext = 'html'):
        """
        Return photo filename for given type of photo.

        For example for dsc_0000 thumbnail we return

            dsc_0000.thumb.html
        """
        return '%s.%s.%s' % (photo.file, photo_type, ext)


    def generate(self):
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        f = File('%s/index.html' % self.outdir)

        pre, post = self.gtmpl.body(self.gallery)
        f.write(pre, post)

        pre, post = self.gtmpl.title(self.gallery)
        f.write(pre)
        f.write(post)

        pre, post = self.gtmpl.albums(self.gallery)
        f.write(pre, post)

        def gen_index(context):
            for album in context.subalbums:
                pre, post = self.gtmpl.album(album)
                f.write(pre)
                gen_index(album)
                f.write(post)
        gen_index(self.gallery)

        f.close()

        for album in self.gallery.subalbums:
            self.generateAlbum(album, self.gallery)


    def generateNavigation(self, f, tmpl, item, data, *tmpl_args):
        pre, post = tmpl.navigation(item, data, *tmpl_args)
        f.write(pre)
        f.write(post)


    def getPrevAndNext(self, items, item, f, *args):
        prev_item = next_item = None
        prev_url = next_url = None
        prev_title = next_title = None

        index = items.index(item)
        if index > 0:
            prev_item = items[index - 1]
        if index < len(items) - 1:
            next_item = items[index + 1]

        if prev_item:
            prev_url = f(prev_item, *args)
            prev_title = prev_item.title
        if next_item:
            next_url = f(next_item, *args)
            next_title = next_item.title

        if isinstance(item, Album):
            next_title = 'next album: %s' % next_title
            prev_title = 'previous album: %s' % prev_title
        elif isinstance(item, Photo):
            next_title = 'next photo: %s' % next_title
            prev_title = 'previous photo: %s' % prev_title
        else:
            assert False, 'only Albums and Photos are supported'

        return {
            'prev_title': prev_title,
            'prev_item': prev_url,
            'next_title': next_title,
            'next_item': next_url,
        }


    def processAlbumNavigation(self, f, album, parent):
        def get_fn(album):
            return '%s/%s/index.html' % (album.gallery.rootdir(album), album.dir)

        subalbums = parent.subalbums
        if isinstance(parent, Gallery):
            ptitle = 'gallery: %s' % parent.title
        else:
            ptitle = 'album: %s' % parent.title

        data = self.getPrevAndNext(subalbums, album, get_fn)
        data['parent'] = '../index.html'
        data['parent_title'] = ptitle
        self.generateNavigation(f, self.atmpl, album, data)


    def processPhotoNavigation(self, f, photo, photo_type):
        data = self.getPrevAndNext(photo.album.photos, photo, self.getPhotoFile, photo_type)
        data['parent'] = 'index.html'
        data['parent_title'] = 'album: %s' % photo.album.title
        self.generateNavigation(f, self.ptmpl, photo, data, photo_type)


    def generateSubalbums(self, f, album):
        """
        Write list of album subalbums.
        """
        if album.subalbums:
            apre, apost = self.atmpl.albums(album)
            f.write(apre)

            for subalbum in album.subalbums:
                pre, post = self.atmpl.album(subalbum)
                f.write(pre)
                f.write(post)
            f.write(apost)


    def generateAlbum(self, album, parent):
        self.fm.mkdir(self.getDir(album))
        f = File(self.getFile(album, 'index.html'))

        pre, post = self.atmpl.body(album)
        f.write(pre, post)

        pre, post = self.atmpl.title(album)
        f.write(pre)
        f.write(post)

        if album.description:
            pre, post = self.atmpl.description(album)
            f.write(pre)
            f.write(post)

        self.processAlbumNavigation(f, album, parent)
        self.generateSubalbums(f, album)

        if album.photos:
            pre, post = self.atmpl.photos(album)
            f.write(pre, post)

            for photo in album.photos:
                pre, post = self.atmpl.photo(photo)
                f.write(pre)
                f.write(post)

        f.close()

        for subalbum in album.subalbums:
            self.generateAlbum(subalbum, album)

        for photo in album.photos:
            self.generateAlbumPhotos(photo)


    def generateAlbumPhotos(self, photo):
        self.generateExif(photo)
        self.convertPhoto(photo, 'thumb')
        self.convertPhoto(photo, 'preview')
        self.convertPhoto(photo, 'view')

        self.generatePhoto(photo, 'preview')
        self.generatePhoto(photo, 'view')


    def generateExif(self, photo):
        fn = self.fm.lookup(self.indir, photo.file)
        photo.exif = self.fm.getExif(fn, self.exif_headers)

        if photo.exif:
            f = File(self.getFile(photo.album, '%s.exif.html' % photo.file))

            pre, post = self.etmpl.body(photo, 'exif')
            f.write(pre, post)

            pre, post = self.etmpl.title(photo, 'exif')
            f.write(pre)
            f.write(post)

            pre, post = self.etmpl.photo(photo, 'exif')
            f.write(pre)
            f.write(post)

            f.close()



    def convertPhoto(self, photo, photo_type):
        fn_out = '%s/%s/%s' % (self.outdir, photo.album.dir, self.getPhotoFile(photo, photo_type, 'jpg'))
        if os.path.exists(fn_out):
            log.info('skipping %s' % fn_out)
        else:
            log.info('converting %s' % fn_out)
            try :
                # get conversion parameters
                assert photo_type in self.convert_args
                args = self.convert_args[photo_type]

                # lookup input file and convert it into gallery file
                fn_in = self.fm.lookup(self.indir, photo.file)
                self.fm.convert(fn_in, fn_out, args)
            except OSError, msg:
                log.warn('failed conversion %s: %s' % (fn_out, msg))


    def generatePhoto(self, photo, photo_type):

        f = File(self.getFile(photo.album, self.getPhotoFile(photo, photo_type)))

        pre, post = self.ptmpl.body(photo, photo_type)
        f.write(pre, post)

        pre, post = self.ptmpl.title(photo, photo_type)
        f.write(pre)
        f.write(post)

        pre, post = self.ptmpl.description(photo, photo_type)
        f.write(pre)
        f.write(post)

        self.processPhotoNavigation(f, photo, photo_type)
        
        pre, post = self.ptmpl.photo(photo, photo_type)
        f.write(pre)
        f.write(post)

        f.close()


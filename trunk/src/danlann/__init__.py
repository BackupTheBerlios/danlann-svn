import sys
import os
import os.path

from danlann.template import XHTMLGalleryIndexTemplate, XHTMLAlbumIndexTemplate, XHTMLPhotoTemplate, XHTMLExifTemplate
from danlann.bc import Album, Photo
from danlann.filemanager import File


class DanlannGenerator(object):
    """
    Gallery generator.

    @ivar conf: danlann configuration
    @ivar photo_dirs: danlann image input dir

    @ivar inputdirs: gallery input directories
    @ivar outdir: gallery output dir
    @ivar gtmpl: gallery template
    @ivar atmpl: album template
    @ivar ptmpl: photo template
    """
    DEFAULT_CONVERT_OPTS = {
        'thumb':   ['-resize', '128x128>',  '-quality', '90', '-unsharp', '3x3+0.5+0'],
        'preview': ['-resize', '800x600>',  '-quality', '90', '-unsharp', '3x3+0.5+0'],
        'view':    ['-resize', '1024x768>', '-quality', '90', '-unsharp', '3x3+0.5+0'],
    }

    def __init__(self, conf, gallery, fm):
        self.conf = conf
        self.gallery = gallery
        self.inputdirs = self.conf.get('danlann', 'inputdirs').split()
        self.outdir = fm.basedir

        self.exif_headers = ['Image timestamp', 'Exposure time',
            'Aperture', 'Exposure bias', 'Flash', 'Flash bias',
            'Focal length', 'ISO speed', 'Exposure mode', 'Metering mode',
            'White balance']
        if self.conf.has_option('danlann', 'exif'):
            self.exif_headers = [exif.strip() for exif in self.conf.get('danlann', 'exif').split(',')]
        #fixme: logger.info('exif data: %s' % self.exif)

        self.gtmpl = XHTMLGalleryIndexTemplate(conf)
        self.atmpl = XHTMLAlbumIndexTemplate(conf)
        self.ptmpl = XHTMLPhotoTemplate(conf)
        self.etmpl = XHTMLExifTemplate(conf)

        self.fm = fm


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
            self.generateAlbum(album)


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


    def processAlbumNavigation(self, f, album):
        def get_fn(album):
            return '%s/%s/index.html' % (album.gallery.rootdir(album), album.dir)

        parent_album = album.album
        if parent_album:
            subalbums = parent_album.subalbums
            ptitle = 'album: %s' % parent_album.title
        else:
            subalbums = album.gallery.subalbums
            ptitle = 'gallery: %s' % album.gallery.title

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


    def generateAlbum(self, album):
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

        self.processAlbumNavigation(f, album)
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
            self.generateAlbum(subalbum)

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
        fn = self.fm.lookup(self.inputdirs, photo.file)
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
            print 'skipping %s' % fn_out # fixme: use logger
        else:
            try :
                # get conversion parameters
                args = self.conf.get(photo_type, 'params')
                if args:
                    args = args.split()
                else:
                    assert photo_type in self.DEFAULT_CONVERT_OPTS
                    args = self.DEFAULT_CONVERT_OPTS[photo_type]

                # lookup input file and convert it into gallery file
                fn_in = self.fm.lookup(self.inputdirs, photo.file)
                self.fm.convert(fn_in, fn_out, args)
                print 'converted %s -> %s' % (fn_in, fn_out) # fixme: use logger
            except OSError, msg:
                print >> sys.stderr, 'failed %s: %s' % (fn_out, msg) # fixme: use logger


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

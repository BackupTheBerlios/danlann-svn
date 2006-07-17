import os.path
import re
import shutil
import libxml2

import logging
log = logging.getLogger('danlann.filemanager')

class File(object):
    def __init__(self, fn):
        self.f = open(fn, 'w')
        self.stack = []

    def write(self, start, end = None):
        self.f.write(start)
        if end:
            self.stack.append(end)

    def close(self):
        while self.stack:
            self.f.write(self.stack.pop())
        self.f.close()



class FileManager(object):
    """
    File manager performs basic file and photo operations
        - copying
        - converting

    @ivar convert: basic convert arguments for ImageMagick
        or GraphicsMagick
    """
    def __init__(self, graphicsmagick):
        """
        Create file manager.

        @param graphicsmagick: if true, then use GraphicsMagick conversion
            basic arguments
        """
        if graphicsmagick:
            self.convert = ['gm', 'gm', 'convert']
        else:
            self.convert = ['convert', 'convert']


    def mkdir(self, dir):
        """
        Create directory if it does not exist.

        @param dir: directory to create
        """
        if not os.path.exists(dir):
            os.makedirs(dir)


    def walk(self, files, destdir, exclude):
        """
        Return iterator of files to be copied.
        
        Tuple (src, dest) is returned, where src is path to file and dest
        is destination directory.

        @param files:   list of source files
        @param destdir: destination directory
        @param exclude: exclude regular expression
        """
        if not hasattr(files, '__iter__') and isinstance(files, basestring):
            raise ValueError('files should be iterable and not string')

        for fn in files:
            fn = os.path.normpath(fn)

            # amount of path elements to skip for destination
            # as copy css/danlann.css to tmp should result
            # in tmp/danlann.css instead of tmp/css/danlann.css
            skip = len(fn.split(os.path.sep)[:-1])

            walk = []
            if os.path.isdir(fn):
                walk = ((tree[0], tree[2]) for tree in os.walk(fn))
            elif os.path.isfile(fn):
                walk = [[os.path.dirname(fn), [os.path.basename(fn)]]]

            for dir, dir_files in walk:
                dest = os.path.join(destdir, *dir.split(os.path.sep)[skip:])

                for dir_file in dir_files:
                    src = '%s/%s' % (dir, dir_file)
                    if not re.search(exclude, src):
                        log.debug('copying %s %s' % (src, dest))
                        yield src, dest


    def copy(self, files, destdir, exclude):
        for src, dest in self.walk(files, destdir, exclude):
            self.mkdir(dest)
            shutil.copy2(src, dest)


    def getExif(self, fn, headers):
        f = os.popen('exiv2 \'%s\'' % fn)
        exif = []
        for line in f:
            if not line:
                continue
            data = line.split(':')
            field = data[0].strip()
            value = ':'.join(data[1:]).strip()
            if field in headers:
                exif.append((field.strip(), value.strip()))

        exif.sort(key = lambda item: headers.index(item[0]))
        return exif


    def lookup(self, indir, fn):
        """
        Look for input file. Return full filename.
        """
        # fixme: look for a file in all input dirs
        return '%s/%s.jpg' % (indir[0], fn)


    def convert(self, fn_in, fn_out, args):
        """
        Look for input photo file and convert file saving it to specified
        filename.

        @pvar fn_in  : photo to convert
        @pvar fn_out : output filename
        @pvar args   : conversion arguments
        """
        args = self.convert + [fn_in] + args + [fn_out]

        if not os.fork():
            os.execlp(*args)
        else:
            pid, status = os.wait()
            if os.WEXITSTATUS(status):
                raise OSError, 'cannot convert file %s' % fn_in
        log.debug('converted %s -> %s' % (fn_in, fn_out))


    def validate(self, fn):
        """
        Validate XML file.

        XML file has to be file with specified XML document type.

        @param fn: XML filename.
        """
        ctxt = libxml2.createFileParserCtxt(fn)
        ctxt.validate(1)
        ctxt.parseDocument()
        doc = ctxt.doc()
        doc.freeDoc()
        valid = ctxt.isValid() != 0
        del ctxt
        return valid


    def formatXML(self, fn):
        """
        Format XML file.

        @param fn: XML filename.
        """
        ctxt = libxml2.createFileParserCtxt(fn)
        ctxt.parseDocument()
        doc = ctxt.doc()

        # save formatted file
        f = open(fn, 'w')
        buf = libxml2.createOutputBuffer(f, 'UTF-8')
        doc.saveFormatFileTo(buf, 'UTF-8', 1)
        f.close()

        doc.freeDoc()
        del ctxt

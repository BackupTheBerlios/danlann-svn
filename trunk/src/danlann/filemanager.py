import os.path
import re
import shutil
import libxml2

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
    def mkdir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)


    def walk(self, files, destdir, exclude):
        """
        @param files:   source files
        @param destdir: destination directory
        @param exclude: exclude regular expression
        """
        for fn in files.split():
            fn = os.path.normpath(fn)

            walk = []
            if os.path.isdir(fn):
                walk = ((tree[0], tree[2]) for tree in os.walk(fn))
            elif os.path.isfile(fn):
                walk = [[os.path.dirname(fn), [os.path.basename(fn)]]]
            for dir, dir_files in walk:
                dest = '%s/%s' % (destdir, dir)

                for df in dir_files:
                    src = '%s/%s' % (dir, df)
                    if not re.search(exclude, src):
                        print 'copying %s %s' % (src, dest) # fixme: use logger
                        yield src, dest


    def copy(self, files):
        for src, dest in self.walk(files):
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


    def lookup(self, inputdirs, fn):
        """
        Look for input file. Return full filename.
        """
        # fixme: look for a file in all input dirs
        return '%s/%s.jpg' % (inputdirs[0], fn)


    def convert(self, fn_in, fn_out, args):
        """
        Look for input photo file and convert file saving it to specified
        filename.

        @pvar photo: photo to convert
        @pvar fn_out: output filename
        @pvar args: conversion parameters
        """
        args = ['convert', fn_in] + args + [fn_out]

        if not os.fork():
            os.execlp('convert', *args)
        else:
            pid, status = os.wait()
            if os.WEXITSTATUS(status):
                raise OSError, 'cannot convert file %s' % fn_in


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

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

import os.path
import re
import shutil
import sys
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
        - looking for files

    @ivar convert_cmd: basic convert arguments for ImageMagick
        or GraphicsMagick
    """
    def __init__(self, graphicsmagick):
        """
        Create file manager.

        @param graphicsmagick: if true, then use GraphicsMagick conversion
            basic arguments
        """
        if graphicsmagick:
            self.convert_cmd = ['gm', 'gm', 'convert']
        else:
            self.convert_cmd = ['convert', 'convert']


    def mkdir(self, dir):
        """
        Create directory if it does not exist.

        @param dir: directory to create
        """
        if not os.path.exists(dir):
            os.makedirs(dir)


    def walk(self, fn, destdir, exclude):
        """
        Return iterator of files to be copied.
        
        Tuple (src, dest) is returned, where src is path to file and dest
        is destination directory.

        @param fn:      file or directory to be copied
        @param destdir: destination directory
        @param exclude: exclude regular expression
        """
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
                    yield src, dest


    def copy(self, fn, destdir, exclude):
        """
        Copy file or directory to destination directory excluding files
        using regular expression.

        @param fn     : file or directory to be copied
        @param destdir: destination directory
        @param exclude: files to exclude
        """
        for src, dest in self.walk(fn, destdir, exclude):
            self.mkdir(dest)
            shutil.copy2(src, dest)
            log.info('%s copied into %s' % (src, dest))


    def getExif(self, fn, headers):
        """
        Get EXIF data from file.

        Hashtable with EXIF data is returned.

        @param fn:      input file
        @param headers: EXIF headers to be returned
        """
        stdin, f, stderr = os.popen3('exiv2 \'%s\'' % fn)
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

        # report exif problems
        for line in stderr:
            log.warn('exif problem (%s): %s' % (fn, line))
        return exif


    def lookup(self, path, fn):
        """
        Look for a file. Returned string is absolute path to a file
        or directory.

        @param path: list of directories to look for a file in
        @param fn:   a file looked for
        """
        for dir in path:
            name = '%s/%s' % (os.path.abspath(dir), fn) 
            if os.path.exists(name):
                yield name


    def convert(self, fn_in, fn_out, args):
        """
        Convert file saving it to specified filename.

        @pvar fn_in  : input filename
        @pvar fn_out : output filename
        @pvar args   : conversion arguments
        """
        self.execl(self.convert_cmd + [fn_in] + args + [fn_out])
        log.info('converted %s -> %s' % (fn_in, fn_out))


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


    def execl(self, args):
        """
        Execute command using @C{os.exec*}.

        @param args: list with command and command arguments to execute
        """
        pid = os.fork()
        if pid:
            pid, status = os.waitpid(pid, 0)
            errno = os.WEXITSTATUS(status)

            # raise exception using errno from child
            if errno:
                raise OSError(errno, os.strerror(errno))
        else:
            try:
                os.close(1)
                os.close(2)
                os.execlp(*args)
            except OSError, ex:
                sys.exit(ex.errno) # exit with errno
            except:
                sys.exit(4) # otherwise EINTR


    def checkCommand(self, cmd):
        """
        Check if it is possible to execute @C{cmd} command by calling:

            cmd -help

        This way it is possible to check for command existence.

        @param cmd: command to check
        """
        self.execl([cmd, cmd, '-help'])

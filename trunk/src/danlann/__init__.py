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
Danlann processor module.
"""

import os
import os.path
import itertools
from ConfigParser import ConfigParser

from danlann import parser
from danlann.bc import Gallery
from danlann.filemanager import FileManager
from danlann.generator import DanlannGenerator

from danlann.template import XHTMLGalleryIndexTemplate, \
    XHTMLAlbumIndexTemplate, XHTMLPhotoTemplate, XHTMLExifTemplate

import logging
log = logging.getLogger('danlann')

class ConfigurationError(Exception):
    """
    Danlann configuration error.
    
    Exception is thrown, when required configuration variable is missing or
    when configuration variable has improper value.
    """
    pass



class Danlann(object):
    """
    Danlann processor reads configuration and creates all necessary objects
    required for gallery generation.

    Generating gallery is divided to specific tasks
        - read configuration
        - initialize and configure all objects
            - danlann processor
            - generator
            - file manager
            - gallery
          after this stage all objects are configured
        - parse album files; data are stored in gallery data instance
        - copy files using file manager
        - generate gallery with generator object
        - reformat and validate output files if requested

    @ivar validate:  validate generated files
    @ivar libpath:   list of gallery library paths
    @ivar outdir:    output dir, all gallery files go to output directory
    @ivar albums:    list of input album files
    @ivar files:     list of additional gallery files, which should be
                     copied to output directory 
    @ivar exclude:   definition of excluded additional files (regular
                     expression)
                     
    @ivar fm:        file manager
    @ivar gallery:   gallery data
    @ivar generator: gallery generator
    """
    def __init__(self):
        self.validate = False
        self.libpath  = ['.']
        self.outdir   = None
        self.albums   = []
        self.files    = []
        self.exclude  = '.svn|CVS|~$|\.swp$'

        self.fm        = None
        self.gallery   = None
        self.generator = None


    def setConvertArgs(self, conf, photo_type):
        section = 'photo:%s' % photo_type
        for option in ('size', 'quality', 'unsharp', 'params'):
            if conf.has_option(section, option):
                value = conf.get(section, option) 
                self.generator.setConvertArg(photo_type, option, value)


    def readConf(self, fn):
        """
        Read configuration file.

        @param fn: configuration file name

        @return configuration object

        @see ConfigParse
        """
        conf = ConfigParser()
        if not conf.read(fn):
            raise ConfigurationError('config file %s does not exist' % fn)
        return conf


    def initialize(self, conf, validate = None):
        """
        Initialize and configure all required instances like
            - generator
            - file manager
            - gallery

        After this stage all objects should configured including the
        processor. Therefore processor configuration is set in
        initialization method, too.

        @param conf:     configuration object
        @param validate: override validation configuration option
        """
        #
        # configure processor
        #
        if conf.has_option('danlann', 'outdir'):
            self.outdir = conf.get('danlann', 'outdir')
        else:
            raise ConfigurationError('no output directory configuration')

        if conf.has_option('danlann', 'libpath'):
            self.libpath = conf.get('danlann', 'libpath').split(':')

        if validate is None and conf.has_option('danlann', 'validate'):
            self.validate = conf.getboolean('danlann', 'validate')
        else:
            self.validate = validate 

        if conf.has_option('danlann', 'albums'):
            self.albums = conf.get('danlann', 'albums').split()
        else:
            raise ConfigurationError('no input album files configuration')

        if conf.has_option('danlann', 'files'):
            self.files = conf.get('danlann', 'files').split()

        if conf.has_option('danlann', 'exclude'):
            self.exclude = conf.get('danlann', 'exclude')

        #
        # create gallery data instance
        #
        if conf.has_option('danlann', 'title'):
            title = conf.get('danlann', 'title')
        else:
            raise ConfigurationError('no gallery title configuration')

        if conf.has_option('danlann', 'description'):
            description = conf.get('danlann', 'description')
        else:
            description = ''

        self.gallery = Gallery(title, description)

        #
        # create file manager
        #
        gm = True
        if conf.has_option('danlann', 'graphicsmagick'):
            gm = conf.getboolean('danlann', 'graphicsmagick')
        self.fm = FileManager(gm)

        #
        # create gallery generator
        #
        if conf.has_option('danlann', 'indir'):
            indir = conf.get('danlann', 'indir').split(':')
        else:
            raise ConfigurationError('no input directory configured')

        exif_headers = ['Image timestamp', 'Exposure time',
            'Aperture', 'Exposure bias', 'Flash', 'Flash bias',
            'Focal length', 'ISO speed', 'Exposure mode', 'Metering mode',
            'White balance']

        if conf.has_option('danlann', 'exif'):
            headers = conf.get('danlann', 'exif').split(',')
            exif_headers = [exif.strip() for exif in headers]

        self.generator              = DanlannGenerator(self.gallery, self.fm)
        self.generator.indir        = indir
        self.generator.outdir       = self.outdir
        self.generator.exif_headers = exif_headers

        self.setConvertArgs(conf, 'thumb')
        self.setConvertArgs(conf, 'preview')
        self.setConvertArgs(conf, 'view')

        self.generator.gtmpl = XHTMLGalleryIndexTemplate(conf)
        self.generator.atmpl = XHTMLAlbumIndexTemplate(conf)
        self.generator.ptmpl = XHTMLPhotoTemplate(conf)
        self.generator.etmpl = XHTMLExifTemplate(conf)



    def copy(self):
        """
        Copy additional gallery files to gallery output directory.
        """
        assert self.outdir
        assert os.path.exists(self.outdir)

        # lookup for all additional files to be copied
        files = (self.fm.lookup(self.libpath, fn) for fn in self.files)

        # copy found files
        for fn in itertools.chain(*files):
            self.fm.copy(fn, self.outdir, self.exclude)


    def parse(self):
        """
        Parse gallery data.
        """
        # read album files
        for fn in self.albums:
            log.debug('parsing album file %s' % fn)
            f = open(fn)
            parser.parse(self.gallery, f)
            f.close()

        # check gallery data instance
        parser.check(self.gallery)


    def generateGallery(self):
        """
        Generate gallery using gallery generator.
        """
        self.generator.generate()


    def postprocess(self):
        """
        Reformat and validate output files if requested.
        """
        def html_files():
            """
            Get all HTML files.
            """
            for dir, subdirs, files in os.walk(self.outdir):
                for fn in files:
                    if fn.endswith('.html'):
                        yield os.path.join(dir, fn)


        for fn in html_files():
            self.fm.formatXML(fn)

            if self.validate:
                log.info('validating file: %s' % fn)
                if not self.fm.validate(fn):
                    log.error('validating failed: %s' % fn)

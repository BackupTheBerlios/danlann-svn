"""
Danlann processor module.
"""

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
        self.outdir = None
        self.albums = []
        self.files = []
        self.exclude = '.svn|CVS|~$|\.swp$'

        self.fm = None


    def readConf(self, fn):
        """
        Read configuration file.

        @param fn: configuration file name

        @return configuration object

        @see ConfigParse
        """
        conf = ConfigParser()
        if not conf.read(fn):
            raise ValueError('config file %s does not exist' % fn)
        return conf


    def initialize(self, conf):
        """
        Initialize and configure all required instances like
            - generator
            - file manager
            - gallery

        After this stage all objects should configured including the
        processor. Therefore processor configuration is set in
        initialization method, too.

        @param conf: configuration object
        """
        #
        # configure processor
        #
        if conf.has_option('danlann', 'outdir'):
            self.outdir = conf.get('danlann', 'outdir')
        else:
            raise ValueError('no output directory configuration')

        if conf.has_option('danlann', 'validate'):
            self.validate = conf.getboolean('danlann', 'validate')

        if conf.has_option('danlann', 'albums'):
            self.albums = conf.get('danlann', 'albums').split()
        else:
            raise ValueError('no input album files configuration')

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
            raise ValueError('no gallery title configuration')

        if conf.has_option('danlann', 'description'):
            description = conf.get('danlann', 'description')
        else:
            description = ''

        self.gallery = Gallery(title, description)

        #
        # create file manager
        #
        self.fm = FileManager()

        #
        # create gallery generator
        #
        self.generator = DanlannGenerator(gallery, fm)


    def copy(self):
        """
        Copy additional gallery files to gallery output directory.
        """
        if self.files:
            assert self.outdir
            self.fm.copy(self.files, self.outdir, self.exclude)


    def parse(self):
        """
        Parse gallery data.
        """
        # read album files
        for fn in self.albums:
            f = open(fn)
            parser.parse(self.gallery, f)
            f.close()

        # check gallery data instance
        parser.check(self.gallery)


    def generateGallery(self):
        """
        Generate gallery using gallery generator.
        """
        se3lf.generator.generate()


    def postprocess(self)
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
                log.debug('validating file: %s' % fn)
                if not fm.validate(fn):
                    log.debug('validating failed: %s' % fn)

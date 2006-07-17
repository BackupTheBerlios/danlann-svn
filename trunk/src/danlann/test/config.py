"""
Configuration tests.
"""

from ConfigParser import ConfigParser
from StringIO import StringIO
import unittest

from danlann import Danlann

# minimal configuration required by danlann
# see Danlann Manual for specification of minimal configuration
CONF_MIN = """
[danlann]
title     = danlann title test

albums    = a.txt b.txt
indir     = input_dir
outdir    = output_dir
"""

# photo configuration changes
CONF_PHOTO = """
[photo:view]
size    = 11
quality = 91
unsharp = 1

[photo:preview]
size    = 12
quality = 92
unsharp = 2

[photo:thumb]
size    = 13
quality = 93
unsharp = 3
"""

CONF_PHOTO_CLEAR_ARG = """
[photo:view]
unsharp =
"""

CONF_PHOTO_PARAMS = """
[photo:view]
params = -level 2% -dither

[photo:preview]
params = -dither -blur 10

[photo:thumb]
params = -blur 15 -dither
"""

CONF_FILEMANAGER = """
graphicsmagick = False
"""

# configuration data for test cases
# test case name is used as hashtable key
CONFIG_DATA = {}

def config(conf):
    """
    Return function, which set configuration data for given test case.

    It is decorator.

    @param conf: configuration data

    @return: function setting configuration data for a test case
    """
    def set_config(test_case):
        """
        Set configuration data for a test case.

        Configuration data is stored in @C{CONFIG_DATA} global variable.
        """
        CONFIG_DATA[test_case.__name__] = conf
        return test_case

    return set_config



class ConfigTestCase(unittest.TestCase):
    """
    Test file manager directory tree generator.

    Configuration data is set using @C{config} decorator.

    @ivar conf     : test case configuration object
    @ivar processor: Danlann processor
    @ivar generator: Danlann gallery generator

    @see config
    """
    def setUp(self):
        """
        Prepare configuration data and initialize Danlann processor
        for a test case.
        """
        self.conf = ConfigParser()

        # get test case configuration data and read configuration
        test_name = getattr(self, '_TestCase__testMethodName')
        self.conf.readfp(StringIO(CONFIG_DATA[test_name]))

        # initialize processor
        self.processor = Danlann()
        self.processor.initialize(self.conf)
        self.generator = self.processor.generator
        self.filemanager = self.processor.fm


    @config(CONF_MIN)
    def testMinimalConfig(self):
        """minimal and default configuration"""

        self.assertEqual(self.processor.albums, ['a.txt', 'b.txt'])
        self.assertEqual(self.processor.gallery.title, 'danlann title test')
        self.assertEqual(self.generator.indir, ['input_dir'])
        self.assertEqual(self.generator.outdir, 'output_dir')

        # see Danlann Manual for specification of default values
        args = self.generator.convert_args['thumb']
        self.assertEqual(args,
            ['-resize', '128x128>', '-quality', '90', '-unsharp', '3x3+0.5+0'])

        args = self.generator.convert_args['preview']
        self.assertEqual(args,
            ['-resize', '800x600>', '-quality', '90', '-unsharp', '3x3+0.5+0'])

        args = self.generator.convert_args['view']
        self.assertEqual(args,
            ['-resize', '1024x768>', '-quality', '90', '-unsharp', '3x3+0.5+0'])


    @config(CONF_MIN + CONF_PHOTO)
    def testConversionArguments(self):
        """photo conversion arguments"""
        assert self.conf.has_option('photo:view', 'size')

        args = self.generator.convert_args['thumb']
        self.assertEqual(args,
            ['-resize', '13', '-quality', '93', '-unsharp', '3'])

        args = self.generator.convert_args['preview']
        self.assertEqual(args,
            ['-resize', '12', '-quality', '92', '-unsharp', '2'])

        args = self.generator.convert_args['view']
        self.assertEqual(args,
            ['-resize', '11', '-quality', '91', '-unsharp', '1'])


    @config(CONF_MIN + CONF_PHOTO_CLEAR_ARG)
    def testConversionArgumentsClear(self):
        """clearing photo conversion arguments"""
        assert self.conf.has_option('photo:view', 'unsharp')
        assert self.conf.get('photo:view', 'unsharp') == ''

        args = self.generator.convert_args['view']
        self.assertEqual(len(args), 4)
        self.assert_('-unsharp' not in args)
        self.assert_('' not in args)


    @config(CONF_MIN + CONF_PHOTO_PARAMS)
    def testAdditionalParameters(self):
        """additional parameters"""
        assert self.conf.has_option('photo:view', 'params')
        assert self.conf.has_option('photo:preview', 'params')
        assert self.conf.has_option('photo:thumb', 'params')

        args = self.generator.convert_args['thumb']
        self.assertEqual(args,
            ['-resize', '128x128>', '-quality', '90',
                '-blur', '15', '-dither', '-unsharp', '3x3+0.5+0'])

        args = self.generator.convert_args['preview']
        self.assertEqual(args,
            ['-resize', '800x600>', '-quality', '90',
                '-dither', '-blur', '10', '-unsharp', '3x3+0.5+0'])

        args = self.generator.convert_args['view']
        self.assertEqual(args,
            ['-resize', '1024x768>', '-quality', '90',
                '-level', '2%', '-dither', '-unsharp', '3x3+0.5+0'])


    @config(CONF_MIN)
    def testUseGraphicsMagick(self):
        """using GraphicsMagick"""
        assert self.conf.has_option('danlann', 'graphicsmagick')
        self.assertEqual(self.filemanager.convert, ['gm', 'gm', 'convert'])


    @config(CONF_MIN + CONF_FILEMANAGER)
    def testUseImageMagick(self):
        """using ImageMagick"""
        assert self.conf.has_option('danlann', 'graphicsmagick')
        self.assertEqual(self.filemanager.convert, ['convert', 'convert'])



if __name__ == '__main__':
    unittest.main()

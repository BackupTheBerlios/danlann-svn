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
Configuration tests.
"""

from ConfigParser import ConfigParser
from StringIO import StringIO
import unittest

import danlann.config
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

CONF_PATHS = """
[danlann]
title     = danlann title test

albums    = a.txt b.txt
indir     = input_dir1:input_dir2
outdir    = output_dir
libpath   = libpath1:libpath2
"""

CONF_LIBPATH_OVERRIDE = """
[danlann]
title     = danlann title test

albums    = a.txt b.txt
indir     = input_dir1:input_dir2
outdir    = output_dir
libpath   = libpath1:$libpath:libpath2
"""

CONF_FILES_OVERRIDE = """
[danlann]
title     = danlann title test

albums    = a.txt b.txt
indir     = input_dir1:input_dir2
outdir    = output_dir
files     = xx $files ee
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
        try:
            test_name = getattr(self, '_TestCase__testMethodName') # python 2.4
        except AttributeError:
            test_name = getattr(self, '_testMethodName')           # python 2.5
        self.conf.readfp(StringIO(CONFIG_DATA[test_name]))

        # initialize processor
        self.processor = Danlann()
        self.processor.initialize(self.conf)
        self.generator = self.processor.generator
        self.filemanager = self.processor.fm


    @config(CONF_MIN)
    def testMinimalConfig(self):
        """minimal and default configuration"""

        self.assertEqual(self.processor.libpath, [danlann.config.libpath])
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


    @config(CONF_PATHS)
    def testPaths(self):
        """paths"""
        assert self.conf.has_option('danlann', 'libpath')
        assert self.conf.has_option('danlann', 'indir')
        self.assertEqual(self.processor.libpath, ['libpath1', 'libpath2'])
        self.assertEqual(self.generator.indir, ['input_dir1', 'input_dir2'])


    @config(CONF_LIBPATH_OVERRIDE)
    def testLibPath(self):
        """libpath override"""
        assert self.conf.has_option('danlann', 'libpath')
        self.assertEqual(self.processor.libpath,
                ['libpath1', danlann.config.libpath, 'libpath2'])


    @config(CONF_FILES_OVERRIDE)
    def testFiles(self):
        """files override"""
        assert self.conf.has_option('danlann', 'files')
        self.assertEqual(self.processor.files,
                ['xx', 'css', 'js', 'ee'])


    @config(CONF_MIN)
    def testUseGraphicsMagick(self):
        """using GraphicsMagick"""
        assert not self.conf.has_option('danlann', 'graphicsmagick')
        self.assertEqual(self.filemanager.convert_cmd, ['gm', 'gm', 'convert'])


    @config(CONF_MIN + CONF_FILEMANAGER)
    def testUseImageMagick(self):
        """using ImageMagick"""
        assert self.conf.has_option('danlann', 'graphicsmagick')
        self.assertEqual(self.filemanager.convert_cmd, ['convert', 'convert'])



class ValidationConfigTestCase(unittest.TestCase):
    """
    Test validation configuration option overriding.
    """
    def testDefaultValidationConfig(self):
        """default validation configuration"""
        conf = ConfigParser()
        conf.readfp(StringIO(CONF_MIN))
        assert not conf.has_option('danlann', 'validate')

        processor = Danlann()
        processor.initialize(conf, False)
        self.assert_(not processor.validate)


    def testValidationConfigOverrideTrue(self):
        """override validation configuration to true"""
        conf = ConfigParser()
        conf.readfp(StringIO(CONF_MIN + '\nvalidate = False'))
        assert not conf.getboolean('danlann', 'validate')

        processor = Danlann()
        processor.initialize(conf, True)
        self.assert_(processor.validate)


    def testValidationConfigOverrideFalse(self):
        """override validation configuration to false"""
        conf = ConfigParser()
        conf.readfp(StringIO(CONF_MIN + '\nvalidate = True'))

        assert conf.getboolean('danlann', 'validate')

        processor = Danlann()
        processor.initialize(conf, False)
        self.assert_(not processor.validate)


if __name__ == '__main__':
    unittest.main()

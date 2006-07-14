"""
Configuration tests.
"""

from ConfigParser import ConfigParser
from StringIO import StringIO
import unittest

from danlann import Danlann

# minimal configuration required by danlann
# see Danlann Manual for specification of minimal configuration
min_conf = """
[danlann]
title     = danlann title test

albums    = a.txt b.txt
inputdirs = input_dir
outdir    = output_dir
"""

# photo configuration changes
photo_conf = """
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

def get_conf(data):
    conf = ConfigParser()
    conf.readfp(StringIO(data))
    return conf


class ConfigTestCase(unittest.TestCase):
    """
    Test file manager directory tree generator.
    """

    def testMinimalConfig(self):
        """minimal and default configuration"""
        processor = Danlann()
        processor.initialize(get_conf(min_conf))

        generator = processor.generator

        self.assertEqual(processor.albums, ['a.txt', 'b.txt'])
        self.assertEqual(processor.gallery.title, 'danlann title test')
        self.assertEqual(generator.inputdirs, ['input_dir'])
        self.assertEqual(generator.outdir, 'output_dir')

        # see Danlann Manual for specification of default values
        self.assertEqual(generator.convert_args['thumb'][1], '128x128>')
        self.assertEqual(generator.convert_args['thumb'][3], '90')
        self.assertEqual(generator.convert_args['thumb'][5], '3x3+0.5+0')
        self.assertEqual(generator.convert_args['preview'][1], '800x600>')
        self.assertEqual(generator.convert_args['preview'][3], '90')
        self.assertEqual(generator.convert_args['preview'][5], '3x3+0.5+0')
        self.assertEqual(generator.convert_args['view'][1], '1024x768>')
        self.assertEqual(generator.convert_args['view'][3], '90')
        self.assertEqual(generator.convert_args['view'][5], '3x3+0.5+0')


    def testConversionArguments(self):
        """conversion arguments"""
        processor = Danlann()
        conf = get_conf(min_conf + photo_conf)

        assert conf.has_option('photo:view', 'size')

        processor.initialize(conf)

        generator = processor.generator

        self.assertEqual(generator.convert_args['thumb'][1], '13')
        self.assertEqual(generator.convert_args['thumb'][3], '93')
        self.assertEqual(generator.convert_args['thumb'][5], '3')
        self.assertEqual(generator.convert_args['preview'][1], '12')
        self.assertEqual(generator.convert_args['preview'][3], '92')
        self.assertEqual(generator.convert_args['preview'][5], '2')
        self.assertEqual(generator.convert_args['view'][1], '11')
        self.assertEqual(generator.convert_args['view'][3], '91')
        self.assertEqual(generator.convert_args['view'][5], '1')


if __name__ == '__main__':
    unittest.main()


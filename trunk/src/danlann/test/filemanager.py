"""
File manager tests.
"""

import re
import unittest

from danlann.filemanager import FileManager

class WalkTestCase(unittest.TestCase):
    """
    Test file manager directory tree generator.
    """

    exclude = '.svn|~$|CVS|.sw[op]$'

    def testDirWalk(self):
        """directory walking"""
        fm = FileManager()
        for src, dest in fm.walk(['css'], 'tmp', self.exclude):
            self.assert_(not re.search('.svn', src))

        walk1 = tuple(fm.walk(['css'], 'tmp', self.exclude))
        walk2 = tuple(fm.walk(['css/'], 'tmp', self.exclude))
        self.assertEqual(walk1, walk2)

        src, dest = list(fm.walk(['src/danlann'], 'tmp', self.exclude))[0]
        self.assert_(dest.startswith('tmp/danlann'))

        src, dest = list(fm.walk(['src/danlann/test'], 'tmp', self.exclude))[0]
        self.assert_(dest.startswith('tmp/test'))


    def testFileWalk(self):
        """file walking"""
        fm = FileManager()

        walk = list(fm.walk(['css/danlann.css'], 'tmp', self.exclude))
        src, dest = walk[0]

        self.assertEqual(len(walk), 1)
        self.assertEqual(src, 'css/danlann.css')
        self.assertEqual(dest, 'tmp')


if __name__ == '__main__':
    unittest.main()

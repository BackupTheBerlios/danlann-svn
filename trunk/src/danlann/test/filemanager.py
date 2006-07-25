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
File manager tests.
"""

import re
import os
import os.path
import unittest

from danlann.filemanager import FileManager

class WalkTestCase(unittest.TestCase):
    """
    Test file manager directory tree generator.
    """

    exclude = '.svn|~$|CVS|.sw[op]$'

    def testDirWalk(self):
        """directory walking"""
        fm = FileManager(True)
        for src, dest in fm.walk('css', 'tmp', self.exclude):
            self.assert_(not re.search('.svn', src))

        walk1 = tuple(fm.walk('css', 'tmp', self.exclude))
        walk2 = tuple(fm.walk('css/', 'tmp', self.exclude))
        self.assertEqual(walk1, walk2)

        src, dest = list(fm.walk('src/danlann', 'tmp', self.exclude))[0]
        self.assert_(dest.startswith('tmp/danlann'))

        src, dest = list(fm.walk('src/danlann/test', 'tmp', self.exclude))[0]
        self.assert_(dest.startswith('tmp/test'))


    def testFileWalk(self):
        """file walking"""
        fm = FileManager(True)

        walk = list(fm.walk('css/danlann.css', 'tmp', self.exclude))
        src, dest = walk[0]

        self.assertEqual(len(walk), 1)
        self.assertEqual(src, 'css/danlann.css')
        self.assertEqual(dest, 'tmp')



class LookupTestCase(unittest.TestCase):
    """
    File lookup tests.
    """
    def testSingleLookup(self):
        """single file lookup"""
        fm = FileManager(True)
        fn = list(fm.lookup(['src'], 'danlann'))[0]
        self.assertEqual(fn, os.path.join(os.getcwd(), 'src', 'danlann'))


    def testLibraryLookup(self):
        """library file lookup"""

        # try to find filemanager.py in src/danlann and src/danlann/test
        # directories
        assert os.path.exists('src/danlann')
        assert os.path.exists('src/danlann/test')
        assert os.path.exists('src/danlann/filemanager.py')
        assert os.path.exists('src/danlann/test/filemanager.py')

        fm = FileManager(True)
        libpath = ('src/danlann', 'src/danlann/test')
        files = list(fm.lookup(libpath, 'filemanager.py'))
        self.assertEqual(files[0], os.path.join(os.getcwd(), 'src/danlann/filemanager.py'))
        self.assertEqual(files[1], os.path.join(os.getcwd(),
            'src/danlann/test/filemanager.py'))



if __name__ == '__main__':
    unittest.main()

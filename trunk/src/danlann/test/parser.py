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

import StringIO
import unittest

from danlann.parser import parse, reset, check, ParseError
from danlann.bc import Gallery

class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.gallery = Gallery('title', 'desc')


    def tearDown(self):
        self.gallery = None
        reset()


    def getFile(self, buf):
        """
        Create StringIO based file using buffer.
        
        Attribute @C{name} is assigned to created file object to support
        file interface as it is used by Danlann parser.
        """
        f = StringIO.StringIO(buf)
        f.name = 'test'
        return f


    def testParser(self):
        """basic parser test"""

        f = self.getFile("""\
# comment
/album1; test; desc1

/album2; test
/album1
photo_a1; title; desc ###
photo_a2; title; desc http://www.danlann.org
photo_a3; title
photo_a4

""")
        parse(self.gallery, f)
        self.assertEquals(len(self.gallery.subalbums), 1)

        a1 = self.gallery.subalbums[0].subalbums[0]
        self.assertEquals(a1.gallery, self.gallery)
        self.assertEquals(a1.dir, 'album1')
        self.assertEquals(len(a1.photos), 0)

        a2 = self.gallery.subalbums[0]
        self.assertEquals(a2.gallery, self.gallery)
        self.assertEquals(a2.dir, 'album2')
        self.assertEquals(len(a2.photos), 4)


    def testReferences(self):
        """references"""

        f = self.getFile("""\
/album1; test; desc1
/album3
/album2
photo_a1; title; desc ###
photo_a2; title; desc http://www.danlann.org

/album2; album 2; this album no 2.
/album3
photo_a3; title
photo_a4

/album3; album 3
photo_a3; title
photo_a4

""")
        parse(self.gallery, f)
        a1 = self.gallery.subalbums[0]
        a3, a2 = a1.subalbums
        self.assertEquals(a1.dir, 'album1')
        self.assertEquals(a2.dir, 'album2')
        self.assertEquals(a3.dir, 'album3')


    def testNoRootAlbumError(self):
        """no root album error"""
        f = self.getFile("""\
/album1; test; desc1
/album2

/album2; album 2; this album no 2.
/album3

/album3; album 3
/album1
""")
        parse(self.gallery, f)
        self.failUnlessRaises(ParseError, check, self.gallery)


    def testNoItemError(self):
        """no item error"""
        f = self.getFile("""\
/album1; test; desc1
photo
/album2; album 2; this album no 2.
photo
/album3; album 3
""")
        parse(self.gallery, f)
        self.failUnlessRaises(ParseError, check, self.gallery)


    def testNotExistingReferenceError(self):
        """ non-existing references error"""

        f = self.getFile("""\
/album1; test; desc1
/album2
photo_a1; title; desc ###
photo_a2; title; desc http://www.danlann.org
""")
        parse(self.gallery, f)
        self.failUnlessRaises(ParseError, check, self.gallery)


    def testDuplicateAlbumError(self):
        """duplicate album error"""

        f = self.getFile("""\
/album1; test; desc1
photo_a1; title; desc ###

/album1; test; duplication
photo_a1; title; desc ###
photo_a2; title; desc http://www.danlann.org
""")
        self.failUnlessRaises(ParseError, parse, self.gallery, f)



if __name__ == '__main__':
    unittest.main()

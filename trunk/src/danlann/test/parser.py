#
# Danlann - Memory Jail - an easy to use photo gallery interpreter.
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

from danlann.parser import DanlannScanner, DanlannParser, \
        interpreter, load, check, ParseError
from danlann.bc import Gallery


class ScannerTestCase(unittest.TestCase):
    def setUp(self):
        self.scanner = DanlannScanner()


    def tokenTypes(self, line):
        return [t.type for t in self.scanner.tokenize(line)]


    def tokenValues(self, line):
        return [t.value for t in self.scanner.tokenize(line)]


    def testComment(self):
        """comment tokens"""
        tokens = self.tokenTypes('#/a; title; desc')
        self.assertEquals(tokens, ['COMMENT'])

        values = self.tokenValues('#/a; title; desc')
        self.assertEquals(values, ['#/a; title; desc'])


    def testAlbum(self):
        """album tokens"""
        tokens = self.tokenTypes('/a; title; desc')
        self.assertEquals(tokens,
                ['SLASH', 'DIR', 'SEMICOLON', 'STRING', 'SEMICOLON', 'STRING'])

        values = self.tokenValues('/a; title; desc')
        self.assertEquals(values, ['/', 'a', ';', 'title', ';', 'desc'])

        tokens = self.tokenTypes('/a; title')
        self.assertEquals(tokens,
                ['SLASH', 'DIR', 'SEMICOLON', 'STRING'])

        values = self.tokenValues('/adir; title')
        self.assertEquals(values, ['/', 'adir', ';', 'title'])


    def testSubalbum(self):
        """subalbum tokens"""
        tokens = self.tokenTypes('/a')
        self.assertEquals(tokens, ['SLASH', 'DIR'])

        values = self.tokenValues('/adir02')
        self.assertEquals(values, ['/', 'adir02'])


    def testPhoto(self):
        """photo tokens"""
        tokens = self.tokenTypes('abc')
        self.assertEquals(tokens, ['FILE'])

        values = self.tokenValues('abc')
        self.assertEquals(values, ['abc'])

        tokens = self.tokenTypes('abc; title')
        self.assertEquals(tokens, ['FILE', 'SEMICOLON', 'STRING'])

        values = self.tokenValues('abc; title')
        self.assertEquals(values, ['abc', ';', 'title'])

        tokens = self.tokenTypes('abc; title; desc')
        self.assertEquals(tokens,
                ['FILE', 'SEMICOLON', 'STRING', 'SEMICOLON', 'STRING'])

        values = self.tokenValues('abc01; title; desc')
        self.assertEquals(values,
                ['abc01', ';', 'title', ';', 'desc'])


class ParseNodeTestCase(unittest.TestCase):
    """
    Test Node creation by parser.
    """
    def setUp(self):
        self.scanner = DanlannScanner()
        self.parser = DanlannParser()


    def parse(self, line):
        return self.parser.parse(self.scanner.tokenize(line))


    def testAlbum(self):
        """simple album parsing"""
        node = self.parse('/a; title; desc')
        self.assertEquals(node.type, 'album')
        self.assertEquals(node.data, ['a', 'title', 'desc'])

        node = self.parse('/adir; title')
        self.assertEquals(node.type, 'album')
        self.assertEquals(node.data, ['adir', 'title', ''])


    def testSubalbum(self):
        """simple subalbum parsing"""
        node = self.parse('/adir04')
        self.assertEquals(node.type, 'subalbum')
        self.assertEquals(node.data, ['adir04'])


    def testPhoto(self):
        """simple photo parsing"""
        node = self.parse('abc')
        self.assertEquals(node.type, 'photo')
        self.assertEquals(node.data, ['abc', '', ''])

        node = self.parse('abc; title')
        self.assertEquals(node.type, 'photo')
        self.assertEquals(node.data, ['abc', 'title', ''])

        node = self.parse('abc; title; desc')
        self.assertEquals(node.type, 'photo')
        self.assertEquals(node.data, ['abc', 'title', 'desc'])



class GenerateTestCase(unittest.TestCase):
    """
    Test object generation.
    """
    def setUp(self):
        self.gallery = Gallery('title', 'desc')
        self.interpreter = interpreter(self.gallery)


    def tearDown(self):
        self.gallery = None
        

    def generate(self, line):
        tokens = self.interpreter.scanner.tokenize(line)
        ast = self.interpreter.parser.parse(tokens)
        self.interpreter.generate(ast)


    def testNewLine(self):
        """new line"""
        self.generate('\n')


    def testAlbum(self):
        """simple album generating"""
        self.generate('/an_album_01; title 1; desc')
        self.assertEquals(len(self.gallery.subalbums), 1)
        self.assertEquals(self.gallery.subalbums[0].dir, 'an_album_01')

        self.generate('/an_album_02; title 2')
        self.assertEquals(len(self.gallery.subalbums), 2)
        self.assertEquals(self.gallery.subalbums[1].dir, 'an_album_02')


    def testSubalbum(self):
        """simple subalbum generating"""
        self.generate('/adir01; title 3')
        self.generate('/adir')
        self.assertEquals(len(self.gallery.subalbums), 1)
        self.assertEquals(self.gallery.subalbums[0].dir, 'adir01')


    def testPhoto(self):
        """simple photo generating"""
        self.generate('/adir01; title')
        self.generate('/adir')

        self.assertEquals(len(self.gallery.subalbums), 1)

        photos = self.gallery.subalbums[0].photos

        self.generate('abc1')
        self.assertEquals(len(photos), 1)
        self.assertEquals(photos[0].name, 'abc1')
        self.assertEquals(photos[0].title, '')
        self.assertEquals(photos[0].description, '')

        self.generate('abc2; title 4')
        self.assertEquals(photos[1].name, 'abc2')
        self.assertEquals(photos[1].title, 'title 4')
        self.assertEquals(photos[1].description, '')

        self.generate('abc3; title3 4; desc desc')
        self.assertEquals(photos[2].name, 'abc3')
        self.assertEquals(photos[2].title, 'title3 4')
        self.assertEquals(photos[2].description, 'desc desc')



class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.gallery = Gallery('title', 'desc')
        self.interpreter = interpreter(self.gallery)


    def tearDown(self):
        self.gallery = None


    def load(self, f):
        load(f, self.interpreter)


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
/album1/sub1; test; desc1

/album2; test
/album1/sub1
photo_a1; title; desc ###
photo_a2; title; desc http://www.danlann.org
photo_a3; title
photo_a4

""")
        self.load(f)
        check(self.interpreter, self.gallery)
        self.assertEquals(len(self.gallery.subalbums), 1) 
        a1 = self.gallery.subalbums[0].subalbums[0]
        self.assertEquals(a1.gallery, self.gallery)
        self.assertEquals(a1.dir, 'album1/sub1')
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
        self.load(f)
        check(self.interpreter, self.gallery)

        self.assertEquals(len(self.gallery.subalbums), 1)

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
        self.load(f)
        self.failUnlessRaises(ParseError, check, self.interpreter, self.gallery)


    def testNoItemError(self):
        """no item error"""
        f = self.getFile("""\
/album1; test; desc1
photo
/album2; album 2; this album no 2.
photo
/album3; album 3
""")
        self.load(f)
        self.failUnlessRaises(ParseError, check, self.interpreter, self.gallery)


    def testNotExistingReferenceError(self):
        """ non-existing references error"""

        f = self.getFile("""\
/album1; test; desc1
/album2
photo_a1; title; desc ###
photo_a2; title; desc http://www.danlann.org
""")
        self.load(f)
        self.failUnlessRaises(ParseError, check, self.interpreter, self.gallery)


    def testDuplicateAlbumError(self):
        """duplicate album error"""

        f = self.getFile("""\
/album1; test; desc1
photo_a1; title; desc ###

/album1; test; duplication
photo_a1; title; desc ###
photo_a2; title; desc http://www.danlann.org
""")
        self.failUnlessRaises(ParseError, self.load, f)



if __name__ == '__main__':
    unittest.main()

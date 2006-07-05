import StringIO
import unittest

from danlann.parser import parse
from danlann.bc import Gallery

class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.gallery = Gallery()


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
photo_a1; title; desc http://www.danlann.org
photo_a2; title
photo_a2

""")
        parse(self.gallery, f)


    def testReferences(self):
        """references"""
        pass


    def testNoItemError(self):
        """no item error"""
        pass


    def testNotExistingReferenceError(self):
        """ non-existing references error"""
        pass


    def testDuplicateAlbumError(self):
        """duplicate album error"""
        pass



if __name__ == '__main__':
    unittest.main()

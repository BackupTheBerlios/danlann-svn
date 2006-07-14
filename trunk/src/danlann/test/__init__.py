import logging

if __debug__:
    logging.basicConfig(level = logging.DEBUG)


import unittest

if __name__ == '__main__':
    from danlann.test.config import *
    from danlann.test.filemanager import *
    from danlann.test.parser import *
    unittest.main()

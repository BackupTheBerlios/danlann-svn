"""
Danlann gallery parser functions.
"""
import sys
import os

#
# lex tokens definitions
#

tokens = 'FILE', 'DIR', 'STRING', 'SEMICOLON', 'COMMENT'

t_FILE      = r'^[A-Za-z0-9_\-]+'
t_DIR       = r'^/[A-Za-z0-9_\-/]+'
t_SEMICOLON = r';'
t_STRING    = r'[^;]+'
t_COMMENT   = r'^\#.*$'


def t_error(t):
    raise ParseError('%s:%d: illegal character "%s"' \
        % (__filename, __lineno, t.value[0]))

import lex
lex.lex()



#
# yacc parser definitions
#

def p_error(error):
    raise ParseError('%s:%d: syntax error' % (__filename, __lineno))


def p_statement(p):
    """
    statement : album
              | subalbum
              | photo
              | COMMENT
    """
    p[0] = p[1]


def p_subalbum(p):
    """
    subalbum : DIR
    """
    album = get_album(p[1])
    p[0] = album

    # if album is not stored then save it in references hashtable;
    # function p_album removes it from the references hashtable as it
    # creates the album
    if album.dir not in __store:
        __references[album.dir] = album
    __album.subalbums.append(album)


def p_album(p):
    """
    album : DIR SEMICOLON STRING
          | DIR SEMICOLON STRING SEMICOLON STRING
    """
    global __album

    album = get_album(p[1])
    album.title = p[3]
    if len(p) == 6:
        album.description = p[5]
    p[0] = album

    # remove album from references as it is defined now;
    # see p_subalbum function 
    if album.dir in __references:
        del __references[album.dir]

    # store new album and set current one
    __store[album.dir] = album
    __album = album


def p_photo(p):
    """
    photo : FILE
          | FILE SEMICOLON STRING
          | FILE SEMICOLON STRING SEMICOLON STRING
    """
    photo = Photo()
    p[0] = photo
    photo.file = p[1]
    if len(p) > 2:
        photo.title = p[3]
    else:
        photo.title = ''
    if len(p) > 4:
        photo.description = p[5]
    __album.photos.append(photo)
    photo.album = __album
    photo.gallery = __gallery



import yacc
yacc.yacc()



#
# parser utility functions and variables
#
from danlann.bc import Gallery, Album, Photo

# hashtable of albums (dir: album)
__store = {}
# hashtable of albums, which are referenced but not yet defined
# (dir: album)
__references = {}

def get_album(dir):
    """
    Return an album object for specified directory.

    If album is not found in reference hashtable nor in store, then new
    album is created.
    """
    dir = os.path.normpath(dir)
    if dir in __references:
        album = __references[dir]
    elif dir in __store:
        album = __store[dir]
    else:
        album = Album()
        album.dir = dir
        album.gallery = __gallery

        # root album directories do not contain slash,
        # store them in gallery
        if '/' not in dir[1:]:
            __gallery.subalbums.append(album)

    return album



#
# parser interface and exceptions
#

class ParseError(Exception):
    """
    Parsing exception.
    """
    pass



def parse(gallery, f):
    """
    Parse album file.

    @param gallery: gallery object
    @param f: album file
    """
    global __album, __gallery, __lineno, __filename

    __gallery = gallery   # gallery object
    __album = None        # current album
    __lineno = 0
    __filename = f.name

    for line in f:
        line = line.strip()
        __lineno += 1
        if line:
            yacc.parse(line)

__all__ = [parse, ParseError]

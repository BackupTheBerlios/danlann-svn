"""
Danlann gallery parser functions.
"""
import sys
import os

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

    # remove album from references as it is defined, now
    if album.dir in __references:
        del __references[album.dir]

    # set current album and store album it
    __store[album.dir] = album
    __album = album


def p_photo(p):
    """
    photo : FILE
          | FILE SEMICOLON STRING
          | FILE SEMICOLON STRING SEMICOLON STRING
    """
    p[0] = p[1]



import yacc

########
from danlann.bc import Gallery, Album, Photo

__store = {}
__references = {}

class ParseError(Exception):
    pass

def get_album(dir):
    dir = os.path.normpath(dir)
    if dir in __references:
        album = __references[dir]
    elif dir in __store:
        album = __store[dir]
    else:
        album = Album()
        album.dir = dir
        # root album directories do not contain slash,
        # store them in gallery
        if '/' not in dir:
            __gallery.subalbums.append(album)

    return album
########


yacc.yacc()

def parse(gallery, f):
    """
    Parse album file.
    """
    global __album, __gallery, __lineno, __filename

    __gallery = gallery
    __album = None
    __lineno = 0
    __filename = f.name

    for line in f:
        line = line.strip()
        __lineno += 1
        if line:
            yacc.parse(line)

__all__ = [parse, ParseError]

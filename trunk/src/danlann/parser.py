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
Danlann gallery parser classes.
"""
import sys
import os
from spark import GenericScanner, GenericParser, GenericASTTraversal

from danlann.bc import Gallery, Album, Photo


FILE, DIR, STRING, COMMENT, SLASH, SEMICOLON, EMPTY= \
        'FILE', 'DIR', 'STRING', 'COMMENT', 'SLASH', 'SEMICOLON', 'EMPTY'

class Token(object):
    """
    Token class with type and value.

    @ivar type:  token type
    @ivar value: token value
    """
    def __init__(self, type, value):
        self.type  = type
        self.value = value


    def __cmp__(self, o):
        return cmp(self.type, o)


    def __str__(self):
        return self.value



class Node(list):
    """
    Parsed album file data.

    @ivar type: node type
    @ivar data: node data, i.e. photo name, title, description
    """
    def __init__(self, type, data = []):
        self.type = type
        self.data = data



class DanlannScanner(GenericScanner):
    """
    Danlann album file scanner.
    """
    def tokenize(self, line):
        self.rv = []
        GenericScanner.tokenize(self, line)
        return self.rv


    def t_SLASH(self, value):
        r'/'
        t = Token(SLASH, value)
        self.rv.append(t)


    def t_SEMICOLON(self, value):
        r'; '
        t = Token(SEMICOLON, value)
        self.rv.append(t)


    def t_FILE(self, value):
        r'(?<=^)[A-Za-z0-9_]+'
        t = Token(FILE, value)
        self.rv.append(t)


    def t_DIR(self, value):
        r'(?<=^/)[A-Za-z0-9_/]+'
        t = Token(DIR, value)
        self.rv.append(t)


    def t_STRING(self, value):
        r'(?<=; )[^;]+'
        t = Token(STRING, value.strip())
        self.rv.append(t)


    def t_COMMENT(self, value):
        r'^\#.*'
        t = Token(COMMENT, value)
        self.rv.append(t)


    def t_EMPTY(self, value):
        r'^\s*$'
        t = Token(EMPTY, value)
        self.rv.append(t)


    def error(self, value, pos):
        global filename, lineno
        raise ParseError('%s:%d: syntax error at"' % (filename, lineno))




class DanlannParser(GenericParser):
    """
    Danlann album file parser.
    """
    def __init__(self):
        GenericParser.__init__(self, 'expr')


    def error(self, token):
        global filename, lineno
        raise ParseError('%s:%d: syntax error' % (filename, lineno))


    def parse(self, tokens):
        ast = GenericParser.parse(self, tokens)
        return ast

    def p_expr(self, args):
        """
        expr ::= album
        expr ::= subalbum
        expr ::= photo
        expr ::= comment
        expr ::= empty
        """
        return args[0]


    def p_subalbum(self, args):
        """
        subalbum ::= SLASH DIR
        """
        data = [args[1].value]
        return Node('subalbum', data)


    def p_album(self, args):
        """
        album ::= SLASH DIR SEMICOLON STRING
        album ::= SLASH DIR SEMICOLON STRING SEMICOLON STRING
        """
        data = [args[1].value, args[3].value, '']
        if len(args) > 4:
            data[2] = args[5].value
        return Node('album', data)


    def p_photo(self, args):
        """
        photo ::= FILE
        photo ::= FILE SEMICOLON STRING
        photo ::= FILE SEMICOLON STRING SEMICOLON STRING
        """
        data = [args[0].value, '', '']
        if len(args) > 2:
            data[1] = args[2].value
        if len(args) > 4:
            data[2] = args[4].value
        return Node('photo', data)


    def p_comment(self, args):
        """
        comment ::= COMMENT
        """
        return Node('comment')


    def p_empty(self, args):
        """
        empty ::= EMPTY
        """
        return Node('empty')



class DanlannInterpret(GenericASTTraversal):
    """
    Danlann album file interpreter. Create gallery albums and photos objects.
    """
    def __init__(self, gallery):
        self.gallery    = gallery

        self.album      = None
        self.references = {}
        self.store      = {}

        GenericASTTraversal.__init__(self, None)


    def generate(self, ast):
        """
        Traverse parsed data and create gallery objects.
        """
        self.postorder(ast)


    def n_album(self, node):
        """
        Create album. Set current album.
        """
        album = self.get_album(node)
        self.album = album

        if album.dir in self.store:
            raise ParseError('album "%s" already defined' % album.dir)

        album.title = node.data[1]
        album.description = node.data[2]

        # remove album from references as it is defined now;
        # see n_subalbum method 
        if album.dir in self.references:
            del self.references[album.dir]

        # store new album
        self.store[album.dir] = album


    def n_subalbum(self, node):
        """
        Add subalbum to current album.
        """
        subalbum = self.get_album(node)

        # if album is not stored then save it in references hashtable;
        # method n_album removes it from the references hashtable as it
        # creates the album
        if subalbum.dir not in self.store:
            self.references[subalbum.dir] = subalbum
        self.album.subalbums.append(subalbum)

        # subalbum cannot be root album
        if subalbum in self.gallery.subalbums:
            self.gallery.subalbums.remove(subalbum)
        return subalbum


    def n_photo(self, node):
        """
        Add photo to current album.
        """
        photo             = Photo()
        photo.name        = node.data[0]
        photo.title       = node.data[1]
        photo.description = node.data[2]

        photo.album       = self.album
        photo.gallery     = self.gallery

        self.album.photos.append(photo)


    def n_comment(self, node):
        """
        Process comment node, which is ignored.
        """
        pass


    def n_empty(self, node):
        """
        Process empty node, which is ignored.
        """
        pass


    def get_album(self, node):
        """
        Create an album object for specified directory.

        If album is not found in reference hashtable nor in store, then new
        album is created.
        """
        dir = os.path.normpath(node.data[0])
        if dir in self.references:
            album = self.references[dir]
        elif dir in self.store:
            album = self.store[dir]
        else:
            album = Album()
            album.dir = dir
            album.gallery = self.gallery

            # add every album to root albums by default;
            # n_subalbum method removes an album from gallery subalbums
            # if an album becomes subalbum
            self.gallery.subalbums.append(album)
        return album



class ParseError(Exception):
    """
    Parsing exception. Raised when input data cannot be parse or when
    created gallery data model is inconsistent.
    """
    pass



def interpreter(gallery):
    """
    Get Danlann album file interpreter.
    """
    interpreter = DanlannInterpret(gallery)
    interpreter.scanner = DanlannScanner()
    interpreter.parser = DanlannParser()
    return interpreter


def check(interpreter, gallery):
    """
    Check if gallery is build in appropriate way:
      - there should be at least on root album
      - every album should one or more subalbums or photos
      - there should be no false references to albums
    """
    def check_album(album):
        if len(album.subalbums) == 0 and len(album.photos) == 0:
            raise ParseError('album "%s" contains no subalbums nor photos'
                % album.dir)

    if len(interpreter.references) > 0:
        raise ParseError('unresolved album references found: %s'
            % ''.join(dir for dir in interpreter.references))

    if len(gallery.subalbums) == 0:
        raise ParseError('no root albums in gallery')

    for album in gallery.subalbums:
        check_album(album)


def load(f, interpreter):
    """
    Load album file.

    @param f:           album file
    @param interpreter: Danlann album file interpreter
    """
    global lineno, filename
    lineno = 0
    filename = f.name
    for line in f:
        line = line.strip()
        lineno += 1
        if line:
            tokens = interpreter.scanner.tokenize(line)
            ast = interpreter.parser.parse(tokens)
            interpreter.generate(ast)

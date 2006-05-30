"""
Danlann gallery parser functions.
"""

import os

from danlann.bc import Gallery, Album, Photo


def get_fields(line):
    """
    Get list of fields, which are kept in a line separated by semi-colon.
    Whitespace is stripped from fields.
    """
    return [f.strip() for f in line.split(';')]


def parse_danlann(danlann):
    """
    Parse gallery description and return generator of albums.
    """
    albums = []
    f = open(danlann)
    for line in f:
        # get fields and strip every of them
        fields = get_fields(line)

        album = Album()
        album.title       = fields[2]
        album.description = fields[3]
        album.dir         = os.path.normpath(fields[0])
        album.thumbnail   = fields[1]

        yield album

    f.close()


def parse_photo(album, line):
    """
    Parse photo data from a line. Assign photo to album.
    """
    fields = get_fields(line)

    photo = Photo()
    photo.file        = fields[0]
    photo.title       = fields[1]
    photo.description = fields[2]

    album.photos.append(photo)
    photo.album = album
    photo.gallery = album.gallery

    assert photo.album and photo in album.photos, \
        'photo should be assigned to some album'
    

def parse_album(fn, albums_by_dir):
    """
    Parse album data from file.
    """
    album = None

    f = open(fn)
    for lineno, line in enumerate(f):
        line = line.strip()

        if not line or line[0] == '#':  # skip empty lines or comments
            continue

        if line[-1] == ':':             # line defines album
            album = albums_by_dir[line[:-1]]

        elif album:                     # if an album exists

            if line[0] == '=':          # look for album reference
                key = line[1:]
                if key in albums_by_dir:
                    album.subalbums.append(albums_by_dir[key])
                else:
                    # fixme: raise exception instead
                    print >> sys.stderr, '%s:%d: unknown album "%s"' % (fn, lineno, line)
                    sys.exit(1)
            else:                       # photo reference
                parse_photo(album, line)
        else:
            print 'skip: ' + line
    f.close()


def parse(conf):
    """
    Danlann gallery parser.

    Returns gallery object.

    @pvar danlann: file with gallery description
    @pvar albums: list of files with description of albums
    """
    danlann = conf.get('danlann', 'gallery')
    albums = conf.get('danlann', 'albums').split()

    gallery = Gallery()
    gallery.title = conf.get('danlann', 'title')
    gallery.description = conf.get('danlann', 'description')

    albums_by_dir = {}
    all_albums = []    # we need this variable mainly to keep order of albums

    # parse album definitions
    for album in parse_danlann(danlann):
        albums_by_dir[album.dir] = album
        all_albums.append(album)
        album.gallery = gallery


    # read album files
    for fn in albums:
        parse_album(fn, albums_by_dir)

    # find parent of albums
    for album in all_albums:
        dirs = album.dir.split('/')
        key = '/'.join(dirs[:-1])
        album.album = albums_by_dir.get(key)

    # assign root albums to gallery
    gallery.subalbums = [album for album in all_albums if not album.album]

    return gallery


__all__ = [parse]

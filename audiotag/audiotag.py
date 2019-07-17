'''
Usage:
  audiotag print FILE...
  audiotag interactive FILE...
  audiotag set [--artist=ARTIST|--noartist] [--title=TITLE|--notitle]
               [--album=ALBUM|--noalbum] [--date=DATE|--nodate]
               [--genre=GENRE|--nogenre] [--tracknumber=TRACKNUMBER|--notracknumber]
               [--tracktotal=TRACKTOTAL|--notracktotal] [--discnumber=DISCNUMBER|--nodiscnumber]
               [--disctotal=DISCTOTAL|--nodisctotal] FILE...
  audiotag clean FILE...
  audiotag rename [--pattern=PATTERN] [-f] FILE...
  audiotag copy SOURCEFOLDER DESTFOLDER
  audiotag -h | --help
  audiotag -v | --version

Arguments:
    FILE     List of files to work with
    PATTERN  Formatting string for renaming files
             May contain the following tags
                 {A}   Artist
                 {T}   Title
                 {L}   Album
                 {Y}   Date
                 {G}   Genre
                 {N}   Tracknumber
                 {D}   Discnumber
                 {NT}  Tracktotal
                 {DT}  Disctotal
             Defaults to '{N} - {T}' or '{D}-{N} - {T}' (if {D} is > 1)
    SOURCE   Load files from this directory when copying tags
    DEST     Save the tags to the files in this directory

Options:
  -f --force    Overwrite existing files without confirmations
  -h --help     Show this screen.
  -v --version  Show version.
'''


import math
import sys
import os
from docopt import docopt
import taglib
try:
    import readline #pylint: disable=unused-import
except ImportError:
    print('Module \'readline\' not found')

ARGS = docopt(__doc__, version='audiotag 0.2.1')

def print_mode():
    '''Prints all filenames and their tags and correspondig values.'''
    tracklist = _open_files(ARGS['FILE'])
    for track in tracklist:
        print('Filename: {0}'.format(track.path))
        for tag, value in track.tags.items():
            print('{0}: {1}'.format(tag, value))
        print('')


def interactive_mode():
    tracklist = _open_files(ARGS['FILE'])
    artist = input('Artist: ')
    album = input('Albumtitle: ')
    genre = input('Genre: ')
    date = input('Date: ')
    tracktotal = input('Number of songs: ')
    disctotal = input('Number of discs: ')
    if disctotal == '1':
        discnumber = '1'
    else:
        discnumber = input('Discnumber: ')
    tracknumber = 0
    for track in tracklist:
        tracknumber += 1
        print(track.path)
        title = input('Title: ')
        # Reuse the stuff we asked the user before
        track.tags['ARTIST'] = [artist]
        track.tags['TITLE'] = [title]
        track.tags['ALBUM'] = [album]
        track.tags['DATE'] = [date]
        track.tags['GENRE'] = [genre]
        track.tags['TRACKNUMBER'] = [str(tracknumber)]
        track.tags['DISCNUMBER'] = [discnumber]
        track.tags['TRACKTOTAL'] = [str(tracktotal)]
        track.tags['DISCTOTAL'] = [disctotal]
    # Loop again so the program can be safely aborted still while getting input
    for track in tracklist:
        track.save()


def set_mode():
    tracklist = _open_files(ARGS['FILE'])
    tags = ['ALBUM', 'ARTIST', 'GENRE', 'DATE', 'DISCNUMBER', 'DISCTOTAL', 'TRACKNUMBER',
            'TRACKTOTAL', 'TITLE']
    for track in tracklist:
        modified = False
        for tag in tags:
            positive_opt = '--{}'.format(tag.lower())
            negative_opt = '--no{}'.format(tag.lower())
            if ARGS[negative_opt]:
                try:
                    track.tags.pop(tag)
                    modified = True
                except KeyError:
                    pass
            if ARGS[positive_opt]:
                track.tags[tag] = [ARGS[positive_opt]]
                modified = True
        if modified:
            track.save()


def clean_mode():
    '''Removes all tags from the files except the ENCODER tag (if it exists).'''
    tracklist = _open_files(ARGS['FILE'])
    for track in tracklist:
        try:
            # Keep ENCODER tag if it exists
            new_tags = {'ENCODER': track.tags['ENCODER']}
            track.tags = new_tags
        except KeyError:
            track.tags = {}
        track.save()


def copy_mode():
    srcfiles = _open_files(_list_files(ARGS['SOURCEFOLDER']))
    dstfiles = _open_files(_list_files(ARGS['DESTFOLDER']))
    srcfiles = sorted(srcfiles, key=lambda x: x.path)
    dstfiles = sorted(dstfiles, key=lambda x: x.path)
    if len(srcfiles) != len(dstfiles):
        print('Different number of files in SOURCEFOLDER and DESTFOLDER. Exiting.')
        sys.exit(1)
    for srcfile, dstfile in zip(srcfiles, dstfiles):
        try:
            # srcfile is never saved so this change is not persistent, just simplifies copying
            srcfile.tags['ENCODER'] = dstfile.tags['ENCODER']
        except KeyError:
            # Encoder not present in dstfile, so delete it before copying
            del srcfile.tags['ENCODER']
        dstfile.tags = srcfile.tags
        dstfile.save()


def rename_mode():
    tracklist = _open_files(ARGS['FILE'])
    tracklist_length = len(tracklist)
    for track in tracklist:
        pattern = _get_pattern(track)
        # Map all tags to their keys for easier renaming
        filename_map = _get_filename_map(track, tracklist_length)
        # Create the new filename, without path or file extension
        new_basename = pattern.format(**filename_map)
        # Returns ('/path/to', 'file.flac')
        path, old_fullname = os.path.split(track.path)
        # Returns ('file', '.flac')
        old_basename, extension = os.path.splitext(old_fullname)
        old_name = '{0}/{1}{2}'.format(path, old_basename, extension)
        new_name = '{0}/{1}{2}'.format(path, new_basename, extension)
        if old_name == new_name:
            continue
        if os.path.isfile(new_name) and not ARGS['--force']:
            question = '''File '{0}' already exists.\nOverwrite it? (y/n): '''.format(new_name)
            if not _yes_no(question):
                continue
        os.rename(old_name, new_name)


def _get_filename_map(track, tracklist_length):
    filename_map = {}
    keys = ['A', 'T', 'L', 'Y', 'G', 'N', 'D', 'NO', 'DO']
    tagnames = ['ARTIST', 'TITLE', 'ALBUM', 'DATE', 'GENRE', 'TRACKNUMBER', 'DISCNUMBER',
                'TRACKTOTAL', 'DISCTOTAL']
    try:
        # Calculate number of leading zeros from 'TRACKTOTAL' tag
        padding = int(math.log10(int(track.tags['TRACKTOTAL'][0]))) + 1
    except KeyError as err:
        print('Warning: \'{0}\' is missing tag {1}'.format(track.path, err))
        print('Guessing number of leading zeros from tracklist')
        # Fallback to length of the tracklist if 'TRACKTOTAL' is missing
        padding = int(math.log10(tracklist_length)) + 1

    for key, tag in zip(keys, tagnames):
        try:
            value = track.tags[tag][0].replace('/', '-')
            if tag == 'TRACKNUMBER':
                value = value.zfill(padding)  # Add leading zero(s)
            filename_map[key] = value
        except KeyError as err:
            print('Warning: \'{0}\' is missing tag {1}'.format(track.path, err))
            filename_map[key] = ''
    return filename_map


def _get_pattern(track):
    if not ARGS['--pattern']:
        try:
            if track.tags['DISCTOTAL'][0] == '1':
                return '{N} - {T}'
            return '{D}-{N} - {T}'
        except KeyError:
            return '{N} - {T}'
    else:
        return ARGS['--pattern']


def _yes_no(question):
    '''
    Continuously asks a yes/no question until user input is in [yYnN].
    Returns True or False respectively.
    '''
    yesno_map = {'y': True, 'n': False}
    choice = ''
    while choice not in ['y', 'n']:
        choice = input(question).lower()
    return yesno_map[choice]


def _open_files(filenames):
    '''
    Opens all files in the param filenames with taglib.
    Exits if no files can be opened.
    '''
    filelist = []
    for filename in filenames:
        filename = os.path.abspath(filename)
        try:
            track = taglib.File(filename)
            filelist.append(track)
        except OSError:
            print('Unable to open file \'{0}\''.format(filename))
    # Exit audiotag if no tracks could be opened
    if not filelist:
        print('No files could be opened')
        sys.exit(1)
    return filelist


def _list_files(directory):
    '''
    Returns a list of all the files in a given directory.
    Exits if path does not exist.
    '''
    try:
        directory = os.path.abspath(directory)
        direntries = os.listdir(directory)
    except OSError as err:
        print(err)
        sys.exit(1)
    files = []
    for filename in direntries:
        filepath = "{0}/{1}".format(directory, filename)
        if os.path.isfile(filepath) and not os.path.islink(filepath):
            files.append(filepath)
    return files


def main():
    '''The main function. Starts whatever mode the user specified.'''
    if ARGS['print']:
        print_mode()
    elif ARGS['set']:
        set_mode()
    elif ARGS['clean']:
        clean_mode()
    elif ARGS['interactive']:
        interactive_mode()
    elif ARGS['rename']:
        rename_mode()
    elif ARGS['copy']:
        copy_mode()


if __name__ == '__main__':
    main()

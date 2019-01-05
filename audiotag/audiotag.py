"""
Usage:
  audiotag print FILE...
  audiotag interactive FILE...
  audiotag set [--artist=ARTIST|--noartist] [--title=TITLE|--notitle]
               [--album=ALBUM|--noalbum] [--date=DATE|--nodate]
               [--genre=GENRE|--nogenre]
               [--tracknumber=TRACKNUMBER|--notracknumber]
               [--tracktotal=TRACKTOTAL|--notracktotal]
               [--discnumber=DISCNUMBER|--nodiscnumber]
               [--disctotal=DISCTOTAL|--nodisctotal] FILE...
  audiotag clean FILE...
  audiotag rename [--pattern=PATTERN] [-f] FILE...
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

Options:
  -f --force    Overwrite existing files without confirmations
  -h --help     Show this screen.
  -v --version  Show version.
"""


from docopt import docopt
import math
import os
import sys
import taglib
try:
    import readline #NOQA
except ImportError:
    print("Module 'readline' not found")

args = docopt(__doc__, version='audiotag 0.2.0')
tracklist = []


def print_mode():
    for track in tracklist:
        print('Filename: {0}'.format(track.path))
        for tag, value in track.tags.items():
            print('{0}: {1}'.format(tag, value))
        print('')


def interactive_mode():
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
    tags = ['ALBUM', 'ARTIST', 'GENRE', 'DATE', 'DISCNUMBER', 'DISCTOTAL',
            'TRACKNUMBER', 'TRACKTOTAL', 'TITLE']
    for track in tracklist:
        modified = False
        for tag in tags:
            positive_opt = "--{}".format(tag.lower())
            negative_opt = "--no{}".format(tag.lower())
            if args[negative_opt]:
                try:
                    track.tags.pop(tag)
                    modified = True
                except KeyError:
                    pass
            if args[positive_opt]:
                track.tags[tag] = [args[positive_opt]]
                modified = True
        if modified:
            track.save()


def clean_mode():
    for track in tracklist:
        try:
            # Keep ENCODER tag if it exists
            new_tags = {'ENCODER': track.tags['ENCODER']}
            track.tags = new_tags
        except KeyError:
            track.tags = {}
        track.save()


def rename_mode():
    for track in tracklist:
        pattern = get_pattern(track)
        # Map all tags to their keys for easier renaming
        filename_map = get_filename_map(track)
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
        if os.path.isfile(new_name) and not args['--force']:
            question = """File '{0}' already exists.
Overwrite it? (y/n): """.format(new_name)
            if not yes_no(question):
                continue
        os.rename(old_name, new_name)


def get_filename_map(track):
    filename_map = {}
    keys = ['A', 'T', 'L', 'Y', 'G', 'N', 'D', 'NO', 'DO']
    tagnames = ['ARTIST', 'TITLE', 'ALBUM', 'DATE', 'GENRE', 'TRACKNUMBER',
                'DISCNUMBER', 'TRACKTOTAL', 'DISCTOTAL']
    try:
        # Calculate number of leading zeros from 'TRACKTOTAL' tag
        padding = int(math.log10(int(track.tags['TRACKTOTAL'][0]))) + 1
    except KeyError as err:
        print("Warning: '{0}' is missing tag {1}".format(track.path, err))
        print("Guessing number of leading zeros from tracklist")
        # Fallback to tracklist length if 'TRACKTOTAL' is missing
        padding = int(math.log10(len(tracklist))) + 1

    for k, t in zip(keys, tagnames):
        try:
            value = track.tags[t][0].replace('/', '-')
            if t == "TRACKNUMBER":
                value = value.zfill(padding)  # Add leading zero(s)
            filename_map[k] = value
        except KeyError as err:
            print("Warning: '{0}' is missing tag {1}".format(track.path, err))
            filename_map[k] = ''
    return filename_map


def get_pattern(track):
    if not args['--pattern']:
        try:
            if track.tags['DISCTOTAL'] == '1':
                return '{N} - {T}'
            else:
                return '{D}-{N} - {T}'
        except KeyError:
            return '{N} - {T}'
    else:
        return args['--pattern']


def yes_no(question):
    yesno_map = {'y': True, 'n': False}
    choice = ''
    while choice not in ['y', 'n']:
        choice = input(question).lower()
    return yesno_map[choice]


def open_files():
    for filename in args['FILE']:
        filename = os.path.abspath(filename)
        try:
            track = taglib.File(filename)
            tracklist.append(track)
        except OSError:
            print("Unable to open file '{0}'".format(filename))
    # Exit audiotag if no tracks could be opened
    if not tracklist:
        print("No files could be opened")
        sys.exit(1)
    return tracklist


def main():
    open_files()
    if args['print']:
        print_mode()
    elif args['set']:
        set_mode()
    elif args['clean']:
        clean_mode()
    elif args['interactive']:
        interactive_mode()
    elif args['rename']:
        rename_mode()


if __name__ == "__main__":
    main()

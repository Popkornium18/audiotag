"""

Usage:
  audiotag interactive <FILE>...
  audiotag print <FILE>...
  audiotag clean <FILE>...
  audiotag rename [-p PATTERN] <FILE>...
  audiotag (-h | --help)
  audiotag (-v | --version)

Arguments:
    FILE    List of files to work with
    PATTERN  Formatting string for renaming files
            May contain the following tags
                {L}  Album
                {R}  Artist
                {G}  Genre
                {T}  Title
                {N}  Track
                {D}  Discnumber
                {Y}  Year
            Defaults to '{N} - {T}' or '{D}-{N} - {T}' (if {D} is > 1)

Options:
  -h --help     Show this screen.
  -v --version  Show version.
  -p --pattern   Specify a rename pattern

"""
from docopt import docopt
import math
import os
import sys
import taglib

args = docopt(__doc__, version='audiotag 0.0.2')


# Removes all tags from the file, except the 'ENCODER' tag
def clean_mode(tracklist):
    for track in tracklist:
        try:
            new_tags = {'ENCODER': track.tags['ENCODER']}
            track.tags = new_tags
        except KeyError:
            track.tags = {}
        track.save()


def print_mode(tracklist):
    for track in tracklist:
        print('Filename: {0}'.format(track.path))
        for tag, value in track.tags.items():
            print('{0}: {1}'.format(tag, value))
        print('')


def interactive_mode(tracklist):
    artist = input('Artist: ')
    album = input('Albumtitle: ')
    genre = input('Genre: ')
    date = input('Year: ')
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
        track.tags['ALBUM'] = [album]
        track.tags['ARTIST'] = [artist]
        track.tags['GENRE'] = [genre]
        track.tags['DATE'] = [date]
        track.tags['DISCNUMBER'] = [discnumber]
        track.tags['DISCTOTAL'] = [disctotal]
        track.tags['TRACKNUMBER'] = [str(tracknumber)]
        track.tags['TRACKTOTAL'] = [str(tracktotal)]
        track.tags['TITLE'] = [title]
    # Loop again so the program can be safely aborted still while getting input
    for track in tracklist:
        track.save()


def rename_mode(tracklist):
    if not args['PATTERN']:
        print("omitting 'string' is not implemented yet")
        exit(1)
    padding = int(math.log10(len(tracklist))) + 1
    for track in tracklist:
        filename_map = {}
        try:
            # Load everything that can be used to rename a file in a map
            # and replace '/' to prevent errors
            # Multiple tags are not supported, therefore [0] is used
            filename_map['L'] = track.tags['ALBUM'][0].replace('/', '-')
            filename_map['A'] = track.tags['ARTIST'][0].replace('/', '-')
            filename_map['G'] = track.tags['GENRE'][0].replace('/', '-')
            filename_map['T'] = track.tags['TITLE'][0].replace('/', '-')
            filename_map['N'] = track.tags['TRACKNUMBER'][0].zfill(padding)
            filename_map['D'] = track.tags['DISCNUMBER'][0]
            filename_map['Y'] = track.tags['DATE'][0]
            # Create the new filename, without path or file extension
            new_basename = args['PATTERN'].format(**filename_map)
            # Returns ('/path/to', 'file.flac')
            path, old_fullname = os.path.split(track.path)
            # Returns ('file', '.flac')
            old_basename, extension = os.path.splitext(old_fullname)
            old_name = '{0}/{1}{2}'.format(path, old_basename, extension)
            new_name = '{0}/{1}{2}'.format(path, new_basename, extension)
            os.rename(old_name, new_name)
        except KeyError as err:
            print("Error: '{0}' is missing tag {1}".format(track.path, err))


def open_files():
    tracklist = []
    for filename in args['<FILE>']:
        filename = os.path.abspath(filename)
        try:
            track = taglib.File(filename)
            tracklist.append(track)
        except OSError:
            print("Unable to open file '{0}'".format(filename))
    # Exit audiotag if no tracks could be opened
    if not tracklist:
        sys.exit(1)
    return tracklist


def main():
    tracklist = open_files()
    if args['print']:
        print_mode(tracklist)
    elif args['clean']:
        clean_mode(tracklist)
    elif args['interactive']:
        interactive_mode(tracklist)
    elif args['rename']:
        rename_mode(tracklist)

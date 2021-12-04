"""
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
"""


from docopt import docopt
from audiotag.modes import (
    print_mode,
    set_mode,
    clean_mode,
    rename_mode,
    copy_mode,
    interactive_mode,
)

try:
    import readline  # noqa: F401
except ImportError:
    print("Module 'readline' not found")

args = docopt(__doc__, version="audiotag 0.4.2")


def main() -> int:
    """The main function. Starts whatever mode the user specified."""
    if args["print"]:
        return print_mode(args)
    elif args["set"]:
        return set_mode(args)
    elif args["clean"]:
        return clean_mode(args)
    elif args["interactive"]:
        return interactive_mode(args)
    elif args["rename"]:
        return rename_mode(args)
    elif args["copy"]:
        return copy_mode(args)
    return 1


if __name__ == "__main__":
    main()

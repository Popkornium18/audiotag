from __future__ import annotations
from typing import TYPE_CHECKING
import argparse
import importlib.metadata
from enum import Enum
from audiotag.track import Tag
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

if TYPE_CHECKING:
    from typing import Optional, Sequence


class Mode(Enum):
    CLEAN = "clean"
    COPY = "copy"
    INTERACTIVE = "interactive"
    PRINT = "print"
    RENAME = "rename"
    SET = "set"


def positive_int(string: str) -> int:
    try:
        number = int(string)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected integer, got {string!r}")

    if number <= 0:
        raise argparse.ArgumentTypeError(f"expected positive integer, got {number}")

    return number


def main(argv: Optional[Sequence[str]] = None) -> int:
    """The main function. Starts whatever mode the user specified."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {importlib.metadata.version('audiotag')}",
    )
    sub_commands = parser.add_subparsers(dest="command")
    sub_commands.required = True
    clean_parser = sub_commands.add_parser(
        name=Mode.CLEAN.value, help=f"delete all tags except '{Tag.ENCODER.value}'"
    )
    copy_parser = sub_commands.add_parser(
        name=Mode.COPY.value,
        help="copy the tags from files in one folder to those in another folder",
    )
    interactive_parser = sub_commands.add_parser(
        name=Mode.INTERACTIVE.value,
        help="tag a single album interactively. "
        + "Treats files in subdirectories as different discs.",
    )
    print_parser = sub_commands.add_parser(name=Mode.PRINT.value, help="print all tags")
    rename_parser = sub_commands.add_parser(
        name=Mode.RENAME.value,
        formatter_class=argparse.RawTextHelpFormatter,
        help="rename files based on their tags",
    )
    set_parser = sub_commands.add_parser(name=Mode.SET.value, help="set or delete tags")

    for tag in [
        Tag.ARTIST,
        Tag.TITLE,
        Tag.ALBUM,
        Tag.GENRE,
    ]:
        group = set_parser.add_mutually_exclusive_group()
        group.add_argument(
            f"--{str.lower(tag.value)}",
            action="store",
        )
        group.add_argument(
            f"--no{str.lower(tag.value)}",
            action="store_true",
        )
    for tag in [
        Tag.DATE,
        Tag.TRACKNUMBER,
        Tag.DISCNUMBER,
        Tag.TRACKTOTAL,
        Tag.DISCTOTAL,
    ]:
        group = set_parser.add_mutually_exclusive_group()
        group.add_argument(
            f"--{str.lower(tag.value)}", action="store", type=positive_int
        )
        group.add_argument(
            f"--no{str.lower(tag.value)}",
            action="store_true",
        )

    rename_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing files without confirmations",
    )
    rename_parser.add_argument(
        "-p",
        "--pattern",
        action="store",
        help="""Formatting string for renaming files
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
Defaults to '{N} - {T}' or '{D}-{N} - {T}' (if {D} > 1)""",
    )

    copy_parser.add_argument(
        "SOURCEFOLDER",
        action="store",
        help="Read tags from files in this directory",
    )
    copy_parser.add_argument(
        "DESTFOLDER", action="store", help="Save tags to files in this directory"
    )

    for subparser in {
        clean_parser,
        interactive_parser,
        print_parser,
        rename_parser,
        set_parser,
    }:
        subparser.add_argument("FILE", nargs="+", help="List of files to tag")

    args = vars(parser.parse_args(argv))
    command = args["command"]
    if command == Mode.PRINT.value:
        return print_mode(args)
    elif command == Mode.SET.value:
        return set_mode(args)
    elif command == Mode.CLEAN.value:
        return clean_mode(args)
    elif command == Mode.INTERACTIVE.value:
        return interactive_mode(args)
    elif command == Mode.RENAME.value:
        return rename_mode(args)
    elif command == Mode.COPY.value:
        return copy_mode(args)
    return 1


if __name__ == "__main__":
    exit(main())

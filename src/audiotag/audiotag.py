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

if TYPE_CHECKING:
    from typing import Optional, Sequence, Any


class Mode(Enum):
    value: str
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


class UpdateDict(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: Optional[str] = None,
    ):
        if not isinstance(values, str | int):
            raise argparse.ArgumentTypeError(
                f"expected string or integer, got {values!r}"
            )

        thedict: dict[Tag, str | int] = getattr(namespace, "set_tags")
        thedict.update({Tag[self.dest.upper()]: values})


def make_parser() -> argparse.ArgumentParser:
    """Creates a parser for the audiotag command line interface"""
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
        name=Mode.CLEAN.value, help="delete all tags"
    )
    clean_parser.add_argument(
        "-k",
        "--keep",
        action="append",
        choices=[tag.value for tag in Tag],
        help=f"specify tags to keep. Defaults to '{Tag.ENCODER.value}'",
    )
    clean_parser.set_defaults(keep=[])
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
    set_parser.set_defaults(remove_tags=[])
    set_parser.set_defaults(set_tags={})

    for tag in [
        Tag.ARTIST,
        Tag.ALBUMARTIST,
        Tag.TITLE,
        Tag.ALBUM,
        Tag.GENRE,
    ]:
        group = set_parser.add_mutually_exclusive_group()
        group.add_argument(f"--{str.lower(tag.value)}", type=str, action=UpdateDict)
        group.add_argument(
            f"--no{str.lower(tag.value)}",
            dest="remove_tags",
            action="append_const",
            const=tag,
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
            f"--{str.lower(tag.value)}", type=positive_int, action=UpdateDict
        )
        group.add_argument(
            f"--no{str.lower(tag.value)}",
            dest="remove_tags",
            action="append_const",
            const=tag,
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
        "SOURCE",
        action="store",
        help="Read tags from this file or files in this directory",
    )
    copy_parser.add_argument(
        "DEST", action="store", help="Save tags to this file or files in this directory"
    )

    interactive_parser.add_argument(
        "-c",
        "--compilation",
        action="store_true",
        help="Set a different artist for each track",
    )

    for subparser in {
        clean_parser,
        interactive_parser,
        print_parser,
        rename_parser,
        set_parser,
    }:
        subparser.add_argument("FILE", nargs="+", help="List of files to tag")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """The main function. Starts whatever mode the user specified."""

    args = vars(make_parser().parse_args(argv))
    command = args["command"]
    if command == Mode.PRINT.value:
        return print_mode(args["FILE"])
    elif command == Mode.SET.value:
        return set_mode(
            remove_tags=set(args["remove_tags"]),
            set_tags=args["set_tags"],
            files=args["FILE"],
        )
    elif command == Mode.CLEAN.value:
        return clean_mode(
            files=args["FILE"],
            keep=None if not args["keep"] else {Tag(tag) for tag in args["keep"]},
        )
    elif command == Mode.INTERACTIVE.value:
        return interactive_mode(files=args["FILE"], compilation=args["compilation"])
    elif command == Mode.RENAME.value:
        return rename_mode(
            files=args["FILE"], pattern=args["pattern"], force=args["force"]
        )
    elif command == Mode.COPY.value:
        return copy_mode(src=args["SOURCE"], dst=args["DEST"])
    return 1


if __name__ == "__main__":
    exit(main())

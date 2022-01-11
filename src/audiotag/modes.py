from __future__ import annotations
from pathlib import Path
import sys
from typing import TYPE_CHECKING
import os
from prompt_toolkit import prompt
from audiotag import styles
from audiotag.track import Track, Tag
from audiotag.util import (
    NoSuchDirectoryError,
    NonEmptyValidator,
    NumberValidator,
    formatted_text_from_str,
    yes_no,
    open_tracks,
    list_files,
    strings_to_paths,
    print_to_console,
)

if TYPE_CHECKING:
    from typing import Optional


def print_mode(files: list[str]) -> int:
    """Prints all filenames and their tags and correspondig values."""
    tracklist = open_tracks(strings_to_paths(files))
    for track in tracklist:
        text = track.format_tags(as_html=sys.stdout.isatty())
        print_to_console(text)
    return 0


def interactive_mode(files: list[str]) -> int:
    tracklist: list[Track] = open_tracks(strings_to_paths(files))

    tags: dict[Tag, list[str]] = {
        Tag.ARTIST: list({t.artist[0] for t in tracklist}),
        Tag.ALBUM: list({t.album for t in tracklist}),
        Tag.GENRE: list({t.genre for t in tracklist}),
        Tag.DATE: list({"" if t.date == 0 else str(t.date) for t in tracklist}),
    }
    defaults: dict[Tag, str] = {
        tag: "" if len(value) > 1 else value[0] for tag, value in tags.items()
    }

    artist = prompt(
        message=formatted_text_from_str("<tag>Artist</tag>: "),
        default=defaults[Tag.ARTIST],
        style=styles.style_track,
        validator=NonEmptyValidator(),
    )
    album = prompt(
        message=formatted_text_from_str("<tag>Albumtitle</tag>: "),
        default=defaults[Tag.ALBUM],
        style=styles.style_track,
        validator=NonEmptyValidator(),
    )
    genre = prompt(
        message=formatted_text_from_str("<tag>Genre</tag>: "),
        default=defaults[Tag.GENRE],
        style=styles.style_track,
        validator=NonEmptyValidator(),
    )
    date = int(
        prompt(
            message=formatted_text_from_str("<tag>Date</tag>: "),
            default=defaults[Tag.DATE],
            style=styles.style_track,
            validator=NumberValidator(),
        )
    )

    parent_dirs = {t.path.parent for t in tracklist}
    discs: list[list[Track]] = []
    for parent in sorted(parent_dirs):
        discs.append(sorted([t for t in tracklist if t.path.parent == parent]))

    disctotal = len(discs)
    for discnumber, disc in enumerate(discs, start=1):
        tracktotal = len(disc)
        for tracknumber, track in enumerate(disc, start=1):
            print(track.path.name)
            prefix = f"Disc {discnumber}, "
            title = prompt(
                message=formatted_text_from_str(
                    f"<tag>{prefix if disctotal > 1 else ''}Track {tracknumber}</tag>: "
                ),
                default=track.title,
                style=styles.style_track,
                validator=NonEmptyValidator(),
            )
            track.artist = artist  # type: ignore
            track.title = title
            track.album = album
            track.date = date
            track.genre = genre
            track.tracknumber = tracknumber
            track.discnumber = discnumber
            track.tracktotal = tracktotal
            track.disctotal = disctotal

    # Loop again so the program can be safely aborted still while getting input
    for track in tracklist:
        track.save()
        track.close()
    return 0


def set_mode(
    files: list[str], remove_tags: set[Tag], set_tags: dict[Tag, str | int]
) -> int:
    tracklist = open_tracks(strings_to_paths(files))
    for track in tracklist:
        set_modified = track.set_tags(set_tags)
        del_modified = track.remove_tags(remove_tags)
        if set_modified or del_modified:
            track.save()
        track.close()
    return 0


def clean_mode(files: list[str], keep: Optional[set[Tag]]) -> int:
    """Removes all tags from the files"""
    tracklist = open_tracks(strings_to_paths(files))
    for track in tracklist:
        track.clear_tags(keep=keep)
        track.save()
        track.close()
    return 0


def copy_mode(source: str, dest: str) -> int:
    try:
        srcfiles = sorted(open_tracks(list_files(Path(source))))
        dstfiles = sorted(open_tracks(list_files(Path(dest))))
    except NoSuchDirectoryError as err:
        print(err)
        return 1

    if len(srcfiles) != len(dstfiles):
        print("Different number of files in SOURCEFOLDER and DESTFOLDER. Exiting.")
        return 1
    for srcfile, dstfile in zip(srcfiles, dstfiles):
        dstfile.copy_tags(source=srcfile)
        dstfile.save()
        dstfile.close()
        srcfile.close()
    return 0


def rename_mode(
    files: list[str], pattern: Optional[str] = None, force: bool = False
) -> int:
    tracklist = open_tracks(strings_to_paths(files))
    for track in tracklist:
        new_path = track.path.parent / (
            track.format_filename(pattern) + track.path.suffix
        )
        if track.path == new_path:
            continue
        if new_path.is_file():
            if not force:
                question = (
                    f"File '{str(new_path)}' already exists.\nOverwrite it? (y/n): "
                )
                if not yes_no(question):
                    continue
            os.remove(new_path)
        track.close()
        os.rename(src=track.path, dst=new_path)
    return 0

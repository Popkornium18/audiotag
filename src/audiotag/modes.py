from __future__ import annotations
from pathlib import Path
import sys
from typing import TYPE_CHECKING
import os
from prompt_toolkit.formatted_text import html
from prompt_toolkit.shortcuts.prompt import PromptSession
from audiotag import config, styles
from audiotag.track import TagListInvalidException, Track, Tag, VALUE_SEP
from audiotag.util import (
    ListValidator,
    NoSuchDirectoryError,
    NonEmptyValidator,
    NumberValidator,
    formatted_text_from_str,
    get_toolbar_text,
    yes_no,
    open_tracks,
    list_files,
    strings_to_paths,
    print_to_console,
)

if TYPE_CHECKING:
    from typing import Optional
    from prompt_toolkit.formatted_text.base import FormattedText


def print_mode(files: list[str]) -> int:
    """Prints all filenames and their tags and correspondig values."""
    tracklist = open_tracks(strings_to_paths(files))
    for track in tracklist:
        text = track.format_tags(as_html=sys.stdout.isatty())
        print_to_console(text)
    return 0


def interactive_mode(files: list[str], compilation: bool) -> int:
    tracklist: list[Track] = open_tracks(strings_to_paths(files))

    tags: dict[Tag, list[str]] = {
        Tag.ARTIST: list({VALUE_SEP.join(t.artist) for t in tracklist}),
        Tag.ALBUMARTIST: list({VALUE_SEP.join(t.album_artist) for t in tracklist}),
        Tag.ALBUM: list({t.album for t in tracklist}),
        Tag.GENRE: list({VALUE_SEP.join(t.genre) for t in tracklist}),
        Tag.DATE: list({"" if t.date == 0 else str(t.date) for t in tracklist}),
    }
    defaults: dict[Tag, str] = {
        tag: "" if len(value) > 1 else value[0] for tag, value in tags.items()
    }

    session = PromptSession(editing_mode=config.editing_mode)  # type: ignore[var-annotated]

    def _ask_artist(message: FormattedText, default: str) -> str:
        artist: str = session.prompt(
            message=message,
            default=default,
            style=styles.style_track,
            bottom_toolbar=get_toolbar_text,
            validator=ListValidator(),
        )
        return artist

    artist: list[str] = []
    album_artist: list[str] = []
    if not compilation:
        artist_multiple = _ask_artist(
            message=formatted_text_from_str("<tag>Artist</tag>: "),
            default=defaults[Tag.ARTIST],
        )
        artist = Track.split_tag(artist_multiple)
        if len(artist) == 1:
            album_artist = artist
        else:
            album_artist_multiple = session.prompt(
                message=formatted_text_from_str("<tag>Album Artist</tag>: "),
                default=defaults[Tag.ALBUMARTIST],
                style=styles.style_track,
                validator=ListValidator(),
            )
            album_artist = Track.split_tag(album_artist_multiple)

    else:
        album_artist = ["Various Artists"]

    album = session.prompt(
        message=formatted_text_from_str("<tag>Albumtitle</tag>: "),
        default=defaults[Tag.ALBUM],
        style=styles.style_track,
        validator=NonEmptyValidator(),
    )

    genre_multiple = session.prompt(
        message=formatted_text_from_str("<tag>Genre</tag>: "),
        default=defaults[Tag.GENRE],
        style=styles.style_track,
        bottom_toolbar=get_toolbar_text,
        validator=ListValidator(),
    )
    genre: list[str] = Track.split_tag(genre_multiple)

    date = int(
        session.prompt(
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
            msg_filename: str | html.HTML = (
                html.HTML(f"<b>File</b>: <i>{html.html_escape(track.path.name)}</i>")
                if sys.stdout.isatty()
                else f"File: {track.path.name}"
            )
            print_to_console(text=msg_filename)
            prefix = f"Disc {discnumber}, " if disctotal > 1 else ""
            if compilation:
                msg_artist = (
                    "<tag>" + f"{prefix}" + f"Track {tracknumber}" + " - Artist</tag>: "
                )
                artist_multiple = _ask_artist(
                    message=formatted_text_from_str(msg_artist),
                    default=VALUE_SEP.join(track.artist),
                )
                artist = Track.split_tag(artist_multiple)

            msg_title = (
                "<tag>"
                + f"{prefix}"
                + f"Track {tracknumber}"
                + (" - Title" if compilation else "")
                + "</tag>: "
            )
            title = session.prompt(
                message=formatted_text_from_str(msg_title),
                default=track.title,
                style=styles.style_track,
                validator=NonEmptyValidator(),
            )
            track.artist = artist
            track.album_artist = album_artist
            track.genre = genre
            track.title = title
            track.album = album
            track.date = date
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
        try:
            set_modified = track.set_tags(set_tags)
        except TagListInvalidException as e:
            print(e)
            return 1
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


def copy_mode(src: str, dst: str) -> int:
    src_path = Path(src)
    dst_path = Path(dst)

    if src_path.is_file() and dst_path.is_file():
        try:
            src_file = Track(src_path)
            dst_file = Track(dst_path)
        except OSError as e:
            print(e)
            return 1
        dst_file.copy_tags(source=src_file)
        dst_file.save()
        dst_file.close()
        src_file.close()
        return 0
    elif src_path.is_dir() and dst_path.is_dir():
        try:
            src_files = sorted(open_tracks(list_files(src_path)))
            dst_files = sorted(open_tracks(list_files(dst_path)))
        except NoSuchDirectoryError as err:
            print(err)
            return 1

        if len(src_files) != len(dst_files):
            print("Different number of files in SOURCEFOLDER and DESTFOLDER")
            return 1
        for src_file, dst_file in zip(src_files, dst_files):
            dst_file.copy_tags(source=src_file)
            dst_file.save()
            dst_file.close()
            src_file.close()
        return 0
    else:
        print("Source and destination must either be both files or both directories")
        return 1


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

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
import os
from audiotag.track import Track, Tag
from audiotag.util import (
    NoSuchDirectoryError,
    yes_no,
    open_tracks,
    list_files,
    strings_to_paths,
)

if TYPE_CHECKING:
    from typing import Dict, List, Any, Set, Union


def print_mode(args: Dict[str, Any]) -> int:
    """Prints all filenames and their tags and correspondig values."""
    tracklist = open_tracks(strings_to_paths(args["FILE"]))
    for track in tracklist:
        print(track.format_string())
    return 0


def interactive_mode(args: Dict[str, Any]) -> int:
    tracklist: List[Track] = open_tracks(strings_to_paths(args["FILE"]))
    artist = input("Artist: ")
    album = input("Albumtitle: ")
    genre = input("Genre: ")
    date = int(input("Date: "))
    parent_dirs = {t.path.parent for t in tracklist}
    discs: List[List[Track]] = []
    for parent in sorted(parent_dirs):
        discs.append(sorted([t for t in tracklist if t.path.parent == parent]))

    disctotal = len(discs)
    for discnumber, disc in enumerate(discs, start=1):
        tracktotal = len(disc)
        for tracknumber, track in enumerate(disc, start=1):
            print(track.path.name)
            prefix = f"Disc {discnumber}, "
            title = input(f"{prefix if disctotal > 1 else ''}Track {tracknumber}: ")
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


def set_mode(args: Dict[str, Any]) -> int:
    tracklist = open_tracks(strings_to_paths(args["FILE"]))

    TAGS = {
        Tag.ALBUM,
        Tag.ARTIST,
        Tag.GENRE,
        Tag.DATE,
        Tag.DISCNUMBER,
        Tag.DISCTOTAL,
        Tag.TRACKNUMBER,
        Tag.TRACKTOTAL,
        Tag.TITLE,
    }
    del_tags: Set[Tag] = {tag for tag in TAGS if args[f"no{tag.value.lower()}"]}
    set_tags: Dict[Tag, Union[str, int]] = {}
    for tag in TAGS:
        if args[tag.value.lower()]:
            set_tags[tag] = args[tag.value.lower()]

    for track in tracklist:
        set_modified = track.set_tags(set_tags)
        del_modified = track.remove_tags(del_tags)
        if set_modified or del_modified:
            track.save()
        track.close()
    return 0


def clean_mode(args: Dict[str, Any]) -> int:
    """Removes all tags from the files except the ENCODER tag (if it exists)."""
    tracklist = open_tracks(strings_to_paths(args["FILE"]))
    for track in tracklist:
        track.clear_tags()
        track.save()
        track.close()
    return 0


def copy_mode(args: Dict[str, Any]) -> int:
    try:
        srcfiles = sorted(open_tracks(list_files(Path(args["SOURCEFOLDER"]))))
        dstfiles = sorted(open_tracks(list_files(Path(args["DESTFOLDER"]))))
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


def rename_mode(args: Dict[str, Any]) -> int:
    tracklist = open_tracks(strings_to_paths(args["FILE"]))
    for track in tracklist:
        new_path = track.path.parent / (
            track.format_filename(args["pattern"]) + track.path.suffix
        )
        if track.path == new_path:
            continue
        if new_path.is_file():
            if not args["force"]:
                question = (
                    f"File '{str(new_path)}' already exists.\nOverwrite it? (y/n): "
                )
                if not yes_no(question):
                    continue
            os.remove(new_path)
        track.close()
        os.rename(src=track.path, dst=new_path)
    return 0

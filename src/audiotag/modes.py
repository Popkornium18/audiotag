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
    from typing import Dict, List, Any


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
            prefix = f"(Disc {discnumber}, ) "
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


# TODO: remove access to Track._file
def set_mode(args: Dict[str, Any]) -> int:
    tracklist = open_tracks(strings_to_paths(args["FILE"]))
    TAGS = [
        Tag.ALBUM.value,
        Tag.ARTIST.value,
        Tag.GENRE.value,
        Tag.DATE.value,
        Tag.DISCNUMBER.value,
        Tag.DISCTOTAL.value,
        Tag.TRACKNUMBER.value,
        Tag.TRACKTOTAL.value,
        Tag.TITLE.value,
    ]
    for track in tracklist:
        modified = False
        for tag in TAGS:
            positive_opt = f"--{tag.lower()}"
            negative_opt = f"--no{tag.lower()}"
            if args[negative_opt]:
                try:
                    track._file.tags.pop(tag)
                    modified = True
                except KeyError:
                    pass
            if args[positive_opt]:
                track._file.tags[tag] = [args[positive_opt]]
                modified = True
        if modified:
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


# TODO: remove access to Track._file
def copy_mode(args: Dict[str, Any]) -> int:
    try:
        srcfiles_unsorted = open_tracks(list_files(Path(args["SOURCEFOLDER"])))
        dstfiles_unsorted = open_tracks(list_files(Path(args["DESTFOLDER"])))
    except NoSuchDirectoryError as err:
        print(err)
        return 1

    srcfiles = sorted(srcfiles_unsorted, key=lambda x: x.path)  # type: ignore[no-any-return]
    dstfiles = sorted(dstfiles_unsorted, key=lambda x: x.path)  # type: ignore[no-any-return]

    if len(srcfiles) != len(dstfiles):
        print("Different number of files in SOURCEFOLDER and DESTFOLDER. Exiting.")
        return 1
    for srcfile, dstfile in zip(srcfiles, dstfiles):
        try:
            # srcfile is never saved so this change is not persistent, just simplifies copying
            srcfile._file.tags[Tag.ENCODER.value] = dstfile._file.tags[
                Tag.ENCODER.value
            ]
        except KeyError:
            # Encoder not present in dstfile, so delete it before copying
            srcfile._file.tags.pop(Tag.ENCODER.value, None)
        dstfile._file.tags = srcfile._file.tags
        dstfile.save()
        dstfile.close()
    return 0


def rename_mode(args: Dict[str, Any]) -> int:
    tracklist = open_tracks(strings_to_paths(args["FILE"]))
    for track in tracklist:
        new_path = track.path.parent / (
            track.format_filename(args["--pattern"]) + track.path.suffix
        )
        if track.path == new_path:
            continue
        if new_path.is_file() and not args["--force"]:
            question = f"File '{str(new_path)}' already exists.\nOverwrite it? (y/n): "
            if not yes_no(question):
                continue
        os.rename(src=track.path, dst=new_path)
    return 0

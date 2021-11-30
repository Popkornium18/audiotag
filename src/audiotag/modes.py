from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
import os
from audiotag.track import Track, Tag
from audiotag.util import (
    NoSuchDirectoryError,
    yes_no,
    open_files,
    list_files,
)

if TYPE_CHECKING:
    from typing import Dict, List, Any


# TODO: move to class
def print_mode(args: Dict[str, Any]) -> int:
    """Prints all filenames and their tags and correspondig values."""
    tracklist = open_files(args["FILE"])
    for track in tracklist:
        print(f"Filename: {track.path}")
        for tag, value in track.tags.items():
            print(f"{tag}: {value}")
        print("")
    return 0


def interactive_mode(args: Dict[str, Any]) -> int:
    tracklist: List[Track] = sorted(open_files(args["FILE"]))
    artist = input("Artist: ")
    album = input("Albumtitle: ")
    genre = input("Genre: ")
    date = int(input("Date: "))
    parent_dirs = {t.file.parent for t in tracklist}
    discs: List[List[Track]] = []
    for parent in parent_dirs:
        discs.append([t for t in tracklist if t.file.parent == parent])

    disctotal = len(discs)
    for discnumber, disc in enumerate(discs, start=1):
        tracktotal = len(disc)
        for tracknumber, track in enumerate(disc, start=1):
            print(track.path)
            title = input("Title: ")
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
    tracklist = open_files(args["FILE"])
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
                    track.tags.pop(tag)
                    modified = True
                except KeyError:
                    pass
            if args[positive_opt]:
                track.tags[tag] = [args[positive_opt]]
                modified = True
        if modified:
            track.save()
            track.close()
    return 0


def clean_mode(args: Dict[str, Any]) -> int:
    """Removes all tags from the files except the ENCODER tag (if it exists)."""
    tracklist = open_files(args["FILE"])
    for track in tracklist:
        track.clear_tags()
        track.save()
        track.close()
    return 0


def copy_mode(args: Dict[str, Any]) -> int:
    try:
        srcfiles_unsorted = open_files(list_files(Path(args["SOURCEFOLDER"])))
        dstfiles_unsorted = open_files(list_files(Path(args["DESTFOLDER"])))
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
            srcfile.tags[Tag.ENCODER.value] = dstfile.tags[Tag.ENCODER.value]
        except KeyError:
            # Encoder not present in dstfile, so delete it before copying
            srcfile.tags.pop(Tag.ENCODER.value, None)
        dstfile.tags = srcfile.tags
        dstfile.save()
        dstfile.close()
    return 0


def rename_mode(args: Dict[str, Any]) -> int:
    tracklist = open_files(args["FILE"])
    for track in tracklist:
        new_path = track.file.parent / (
            track.format(args["--pattern"]) + track.file.suffix
        )
        if track.file == new_path:
            continue
        if new_path.is_file() and not args["--force"]:
            question = f"File '{str(new_path)}' already exists.\nOverwrite it? (y/n): "
            if not yes_no(question):
                continue
        os.rename(src=track.file, dst=new_path)
    return 0

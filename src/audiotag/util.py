from __future__ import annotations
from typing import TYPE_CHECKING
from audiotag.track import Track
from pathlib import Path

if TYPE_CHECKING:
    from typing import List


class NoSuchDirectoryError(Exception):
    pass


class NoAudioFilesFoundError(Exception):
    pass


def yes_no(question: str) -> bool:
    """
    Continuously asks a yes/no question until user input is in [yYnN].
    Returns True or False respectively.
    """
    YESNO_MAP = {"y": True, "n": False}
    choice = ""
    while choice not in ["y", "n"]:
        choice = input(question).lower()
    return YESNO_MAP[choice]


def strings_to_paths(strings: List[str]) -> List[Path]:
    """Converts a list of filenames in string form into a list of paths"""
    return [Path(string) for string in strings]


def open_tracks(paths: List[Path]) -> List[Track]:
    """
    Opens all files in the param filenames with taglib.
    Raises NoAudioFilesFoundError if no files can be opened.
    """
    tracks: List[Track] = []
    for path in paths:
        try:
            track = Track(path)
        except OSError:
            print("Unable to open file '{str(path)}'")
            continue
        tracks.append(track)
    if not tracks:
        raise NoAudioFilesFoundError("No files could be opened")
    return tracks


def list_files(directory: Path) -> List[Path]:
    """
    Returns a list of all the files in a given directory.
    Raises DirectoryEmptyError if directory does not exist.
    """
    if not directory.exists() or directory.is_file():
        raise NoSuchDirectoryError(f"Directory '{directory}' does not exist.")

    children = [child for child in directory.iterdir() if child.is_file()]
    return children

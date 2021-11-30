from __future__ import annotations
from typing import TYPE_CHECKING
from audiotag.track import Track

if TYPE_CHECKING:
    from typing import List
    from pathlib import Path


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


def open_files(paths: List[Path]) -> List[Track]:
    """
    Opens all files in the param filenames with taglib.
    Raises NoAudioFilesFoundError if no files can be opened.
    """
    tracks: List[Track] = []
    for path in paths:
        track = Track.open_file(path)
        if track:
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

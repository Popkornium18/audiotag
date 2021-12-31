from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pathlib import Path
import audiotag.util as util

if TYPE_CHECKING:
    from audiotag.track import Track


@pytest.mark.parametrize(
    "input,expected", [("Y", True), ("y", True), ("N", False), ("n", False)]
)
def test_yes_no(monkeypatch: pytest.MonkeyPatch, input: str, expected: bool) -> None:
    monkeypatch.setattr("builtins.input", lambda _: input)
    assert util.yes_no("Testing yes_no: ") == expected


@pytest.mark.usefixtures("mixed_dir")
def test_open_tracks_mixed(mixed_dir: Path) -> None:
    files = util.list_files(mixed_dir)
    assert len(util.open_tracks(files)) == 1


@pytest.mark.usefixtures("image_dir")
def test_open_tracks_invalid(image_dir: Path) -> None:
    files = util.list_files(image_dir)
    with pytest.raises(util.NoAudioFilesFoundError):
        util.open_tracks(files)


@pytest.mark.usefixtures("audio_file")
def test_list_files(audio_file: Track) -> None:
    assert len(util.list_files(audio_file.path.parent)) == 1
    audio_file.close()


def test_list_files_error() -> None:
    with pytest.raises(util.NoSuchDirectoryError):
        len(util.list_files(Path("DOES_DEFINITELY_NOT_EXIST")))


def test_strings_to_paths() -> None:
    strings = ["test1", "test2", "test3"]
    paths = util.strings_to_paths(strings)
    assert strings == [path.name for path in paths]

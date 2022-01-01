from __future__ import annotations
import os
import shutil
from typing import TYPE_CHECKING
import pytest
from audiotag.track import Track, Tag
from audiotag.modes import (
    clean_mode,
    copy_mode,
    interactive_mode,
    print_mode,
    rename_mode,
    set_mode,
)
from conftest import FakeTag

if TYPE_CHECKING:
    from typing import Any


@pytest.mark.parametrize(
    "artists",
    [["lel"], ["lol", "lul"]],
)
@pytest.mark.usefixtures("audio_file")
def test_print_mode(audio_file: Track, artists: list[str], capfd):
    audio_file.artist = artists
    audio_file.save()
    audio_file.close()
    expected = f"""Filename: {str(audio_file.path)}
{Tag.ALBUM.name}: {FakeTag.ALBUM.value}
{Tag.ARTIST.name}: {artists[0] if len(artists) == 1 else artists}
{Tag.DATE.name}: {str(FakeTag.DATE.value)}
{Tag.DISCNUMBER.name}: {str(FakeTag.DISCNUMBER.value)}
{Tag.DISCTOTAL.name}: {str(FakeTag.DISCTOTAL.value)}
{Tag.ENCODER.name}: {FakeTag.ENCODER.value}
{Tag.GENRE.name}: {FakeTag.GENRE.value}
{Tag.TITLE.name}: {FakeTag.TITLE.value}
{Tag.TRACKNUMBER.name}: {str(FakeTag.TRACKNUMBER.value)}
{Tag.TRACKTOTAL.name}: {str(FakeTag.TRACKTOTAL.value)}

"""
    args: dict[str, Any] = {
        "FILE": [str(audio_file.path)],
    }
    error_code = print_mode(args)
    stdout, stderr = capfd.readouterr()
    assert not error_code
    assert not stderr
    assert stdout == expected


@pytest.mark.usefixtures("audio_file")
def test_clean_mode(audio_file: Track):
    audio_file.close()
    args: dict[str, Any] = {
        "FILE": [str(audio_file.path)],
    }
    error_code = clean_mode(args)
    assert not error_code
    cleaned_file = Track(audio_file.path)
    assert cleaned_file
    assert cleaned_file.has_tag(Tag.ENCODER)
    assert not cleaned_file.has_tag(Tag.ALBUM)
    assert not cleaned_file.has_tag(Tag.ARTIST)
    assert not cleaned_file.has_tag(Tag.DATE)
    assert not cleaned_file.has_tag(Tag.DISCNUMBER)
    assert not cleaned_file.has_tag(Tag.DISCTOTAL)
    assert not cleaned_file.has_tag(Tag.GENRE)
    assert not cleaned_file.has_tag(Tag.TITLE)
    assert not cleaned_file.has_tag(Tag.TRACKNUMBER)
    assert not cleaned_file.has_tag(Tag.TRACKTOTAL)
    cleaned_file.close()


def test_copy_mode_dir_not_exist():
    args: dict[str, Any] = {
        "SOURCEFOLDER": "DoesNotExist",
        "DESTFOLDER": "DoesNotExistEither",
    }
    error_code = copy_mode(args)
    assert error_code == 1


@pytest.mark.usefixtures("audio_file")
def test_copy_mode_too_many_files(audio_file: Track):
    audio_file.close()
    src = audio_file.path.parent / "src"
    dst = audio_file.path.parent / "dst"
    os.mkdir(src)
    os.mkdir(dst)
    shutil.copyfile(audio_file.path, src / audio_file.path.name)
    shutil.copyfile(audio_file.path, src / ("lmao" + audio_file.path.suffix))
    shutil.move(audio_file.path, dst / audio_file.path.name)
    args: dict[str, Any] = {
        "SOURCEFOLDER": str(src),
        "DESTFOLDER": str(dst),
    }
    error_code = copy_mode(args)
    assert error_code == 1


@pytest.mark.usefixtures("audio_file")
def test_copy_mode(audio_file: Track):
    src = audio_file.path.parent / "src"
    dst = audio_file.path.parent / "dst"
    os.mkdir(src)
    os.mkdir(dst)
    shutil.copyfile(audio_file.path, src / audio_file.path.name)
    audio_file.clear_tags(keep=set())
    audio_file._file.tags[Tag.ENCODER.value] = ["lol"]
    audio_file.save()
    audio_file.close()
    shutil.move(audio_file.path, dst / audio_file.path.name)
    args: dict[str, Any] = {
        "SOURCEFOLDER": str(src),
        "DESTFOLDER": str(dst),
    }
    error_code = copy_mode(args)
    assert not error_code
    srcfile = Track(src / audio_file.path.name)
    dstfile = Track(dst / audio_file.path.name)
    assert srcfile and dstfile
    assert srcfile.album == dstfile.album
    assert srcfile.artist == dstfile.artist
    assert srcfile.discnumber == dstfile.discnumber
    assert srcfile.disctotal == dstfile.disctotal
    assert srcfile.genre == dstfile.genre
    assert srcfile.title == dstfile.title
    assert srcfile.tracknumber == dstfile.tracknumber
    assert srcfile.tracktotal == dstfile.tracktotal
    assert srcfile.encoder == FakeTag.ENCODER.value
    assert dstfile.encoder == "lol"
    srcfile.close()
    dstfile.close()


@pytest.mark.parametrize(
    "pattern,title,expected",
    [
        ("", FakeTag.TITLE.value, f"1 - {FakeTag.TITLE.value}"),
        ("{T}", "noise", "noise"),
    ],
)
@pytest.mark.usefixtures("audio_file")
def test_rename_mode(
    audio_file: Track,
    pattern: str,
    title: str,
    expected: str,
) -> None:
    audio_file.title = title
    audio_file.save()
    audio_file.close()

    args: dict[str, Any] = {
        "FILE": [str(audio_file.path)],
        "pattern": pattern,
    }

    error_code = rename_mode(args)
    assert not error_code
    new_file = audio_file.path.parent / (expected + audio_file.path.suffix)
    assert new_file.is_file()
    assert new_file.name == expected + audio_file.path.suffix


@pytest.mark.parametrize("force", [True, False])
@pytest.mark.usefixtures("audio_file")
def test_rename_mode_existing(
    audio_file: Track, monkeypatch: pytest.MonkeyPatch, force: bool
):
    audio_file.close()
    copy = audio_file.path.parent / (FakeTag.TITLE.value + audio_file.path.suffix)
    shutil.copyfile(audio_file.path, copy)
    copytrack_before = Track(copy)
    copytrack_before.clear_tags()
    copytrack_before.save()
    copytrack_before.close()

    monkeypatch.setattr("builtins.input", lambda _: "y" if force else "n")

    args: dict[str, Any] = {
        "FILE": [str(audio_file.path)],
        "pattern": "{T}",
        "force": force,
    }
    error_code = rename_mode(args)
    assert not error_code
    copytrack_after = Track(copy)
    assert copytrack_after
    if force:
        assert copytrack_after.title == FakeTag.TITLE.value
    else:
        assert not copytrack_after.title
    copytrack_after.close()


@pytest.mark.usefixtures("audio_file")
def test_interactive_mode(audio_file: Track, monkeypatch: pytest.MonkeyPatch):
    audio_file.clear_tags(keep=set())
    audio_file.save()
    audio_file.close()

    answers = [
        FakeTag.ARTIST.value,
        FakeTag.ALBUM.value,
        FakeTag.GENRE.value,
        str(FakeTag.DATE.value),
        FakeTag.TITLE.value,
    ]
    monkeypatch.setattr("builtins.input", lambda _: answers.pop(0))

    args: dict[str, Any] = {
        "FILE": [str(audio_file.path)],
    }

    error_code = interactive_mode(args)
    assert not error_code
    audio_file_after = Track(audio_file.path)
    assert audio_file_after
    assert audio_file_after.artist == [FakeTag.ARTIST.value]
    assert audio_file_after.album == FakeTag.ALBUM.value
    assert audio_file_after.genre == FakeTag.GENRE.value
    assert audio_file_after.date == FakeTag.DATE.value
    assert audio_file_after.title == FakeTag.TITLE.value
    assert audio_file_after.tracknumber == FakeTag.TRACKNUMBER.value
    assert audio_file_after.tracktotal == FakeTag.TRACKTOTAL.value
    assert audio_file_after.discnumber == FakeTag.DISCNUMBER.value
    assert audio_file_after.disctotal == FakeTag.DISCTOTAL.value
    audio_file_after.close()


@pytest.mark.usefixtures("audio_file")
def test_set_mode(audio_file: Track):
    audio_file.close()
    newartist = "SOMEARTIST"
    newtracknum = 10
    args: dict[str, Any] = {
        "FILE": [str(audio_file.path)],
        Tag.ARTIST.value.lower(): newartist,
        Tag.TRACKNUMBER.value.lower(): newtracknum,
        Tag.ALBUM.value.lower(): None,
        Tag.DATE.value.lower(): None,
        Tag.DISCNUMBER.value.lower(): None,
        Tag.DISCTOTAL.value.lower(): None,
        Tag.GENRE.value.lower(): None,
        Tag.TITLE.value.lower(): None,
        Tag.TRACKTOTAL.value.lower(): None,
        f"no{Tag.TITLE.value.lower()}": True,
        f"no{Tag.ALBUM.value.lower()}": False,
        f"no{Tag.ARTIST.value.lower()}": False,
        f"no{Tag.DATE.value.lower()}": False,
        f"no{Tag.DISCNUMBER.value.lower()}": False,
        f"no{Tag.DISCTOTAL.value.lower()}": False,
        f"no{Tag.GENRE.value.lower()}": False,
        f"no{Tag.TRACKNUMBER.value.lower()}": False,
        f"no{Tag.TRACKTOTAL.value.lower()}": False,
    }
    assert audio_file.has_tag(Tag.TITLE)
    assert not audio_file.artist == [newartist]
    assert not audio_file.tracknumber == newtracknum
    error_code = set_mode(args)
    audio_file = Track(audio_file.path)
    assert not error_code
    assert not audio_file.has_tag(Tag.TITLE)
    assert audio_file.artist == [newartist]
    assert audio_file.tracknumber == newtracknum
    audio_file.close()

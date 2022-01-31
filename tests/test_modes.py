from __future__ import annotations
import os
import shutil
import pytest
from audiotag.track import Track, Tag
from audiotag.modes import (
    clean_mode,
    copy_mode,
    print_mode,
    rename_mode,
    set_mode,
)
from conftest import FakeTag


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
{Tag.ALBUMARTIST.name}: {FakeTag.ALBUMARTIST.value}
{Tag.ARTIST.name}: {artists[0] if len(artists) == 1 else ", ".join(artists)}
{Tag.DATE.name}: {str(FakeTag.DATE.value)}
{Tag.DISCNUMBER.name}: {str(FakeTag.DISCNUMBER.value)}
{Tag.DISCTOTAL.name}: {str(FakeTag.DISCTOTAL.value)}
{Tag.ENCODER.name}: {FakeTag.ENCODER.value}
{Tag.GENRE.name}: {FakeTag.GENRE.value[0]}
{Tag.TITLE.name}: {FakeTag.TITLE.value}
{Tag.TRACKNUMBER.name}: {str(FakeTag.TRACKNUMBER.value)}
{Tag.TRACKTOTAL.name}: {str(FakeTag.TRACKTOTAL.value)}

"""
    error_code = print_mode([str(audio_file.path)])
    stdout, stderr = capfd.readouterr()
    assert not error_code
    assert not stderr
    assert stdout == expected


@pytest.mark.usefixtures("audio_file")
def test_clean_mode(audio_file: Track):
    audio_file.close()
    error_code = clean_mode(files=[str(audio_file.path)], keep=None)
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
    error_code = copy_mode(source="DoesNotExist", dest="DoesNotExistEither")
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
    error_code = copy_mode(source=str(src), dest=str(dst))
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
    error_code = copy_mode(source=str(src), dest=str(dst))
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
    error_code = rename_mode(files=[str(audio_file.path)], pattern=pattern)
    assert not error_code
    new_file = audio_file.path.parent / (expected + audio_file.path.suffix)
    assert new_file.is_file()
    assert new_file.name == expected + audio_file.path.suffix


@pytest.mark.usefixtures("audio_file")
def test_rename_mode_existing(audio_file: Track):
    audio_file.close()
    copy = audio_file.path.parent / (FakeTag.TITLE.value + audio_file.path.suffix)
    shutil.copyfile(audio_file.path, copy)
    copytrack_before = Track(copy)
    copytrack_before.clear_tags()
    copytrack_before.save()
    copytrack_before.close()
    error_code = rename_mode(files=[str(audio_file.path)], pattern="{T}", force=True)
    assert not error_code
    copytrack_after = Track(copy)
    assert copytrack_after
    assert copytrack_after.title == FakeTag.TITLE.value
    copytrack_after.close()


@pytest.mark.usefixtures("audio_file")
def test_set_mode(audio_file: Track):
    audio_file.close()
    newartist = "SOMEARTIST"
    newtracknum = 10
    assert audio_file.has_tag(Tag.TITLE)
    assert not audio_file.artist == [newartist]
    assert not audio_file.tracknumber == newtracknum
    error_code = set_mode(
        files=[str(audio_file.path)],
        remove_tags={Tag.TITLE},
        set_tags={Tag.ARTIST: newartist, Tag.TRACKNUMBER: newtracknum},
    )
    audio_file = Track(audio_file.path)
    assert not error_code
    assert not audio_file.has_tag(Tag.TITLE)
    assert audio_file.artist == [newartist]
    assert audio_file.tracknumber == newtracknum
    audio_file.close()

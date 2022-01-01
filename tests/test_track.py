from __future__ import annotations
from pathlib import Path
import pytest
import shutil
from conftest import FakeTag
from audiotag.track import Track, Tag, Pattern


@pytest.mark.usefixtures("audio_file")
def test_comparison(audio_file: Track):
    audio_file.close()
    copyfile_name = "lol" + audio_file.path.suffix
    shutil.copyfile(audio_file.path, audio_file.path.with_name(copyfile_name))
    audio_file_same = Track(audio_file.path)
    audio_file_different = Track(audio_file.path.with_name(copyfile_name))
    assert audio_file == audio_file_same
    assert audio_file != audio_file_different
    assert audio_file_same > audio_file_different
    assert audio_file_different < audio_file_same
    audio_file_same.close()
    audio_file_different.close()


@pytest.mark.usefixtures("audio_file")
def test_eq_invalid(audio_file: Track):
    audio_file.close()
    (audio_file == object) == NotImplemented


@pytest.mark.usefixtures("audio_file")
def test_sorting(audio_file: Track):
    audio_file.close()
    second = Path(audio_file.path.parent / ("zzzz" + audio_file.path.suffix))
    shutil.copyfile(audio_file.path, second)
    second_file = Track(second)
    assert second_file
    assert sorted([second_file, audio_file]) == [audio_file, second_file]
    second_file.close()


@pytest.mark.usefixtures("audio_file")
def test_repr(audio_file: Track):
    audio_file.close()
    str(audio_file) == f"Track('{str(audio_file.path)}')"


@pytest.mark.usefixtures("audio_file")
def test_has_tag(audio_file: Track):
    audio_file.clear_tags()
    assert audio_file.has_tag(Tag.ENCODER)
    assert not audio_file.has_tag(Tag.ALBUM)
    audio_file.close()


@pytest.mark.usefixtures("audio_file")
def test_clear_tag(audio_file: Track):
    assert audio_file.has_tag(Tag.ENCODER)
    assert audio_file.has_tag(Tag.ARTIST)
    assert audio_file.has_tag(Tag.ALBUM)
    audio_file.clear_tags(keep={Tag.ENCODER, Tag.ALBUM})
    assert audio_file.has_tag(Tag.ENCODER)
    assert audio_file.has_tag(Tag.ALBUM)
    assert not audio_file.has_tag(Tag.ARTIST)
    audio_file.clear_tags()
    assert audio_file.has_tag(Tag.ENCODER)
    assert not audio_file.has_tag(Tag.ALBUM)
    audio_file.clear_tags(keep=set())
    assert not audio_file.has_tag(Tag.ENCODER)
    audio_file.close()


@pytest.mark.usefixtures("audio_file")
def test_encoder(audio_file: Track):
    audio_file.close()
    with pytest.raises(AttributeError):
        audio_file.encoder = "something"  # type: ignore


@pytest.mark.usefixtures("audio_file")
def test_default_tags(audio_file: Track):
    audio_file.clear_tags(keep=set())
    audio_file.close()
    assert audio_file.album == ""
    assert audio_file.genre == ""
    assert audio_file.date == 0
    assert audio_file.title == ""
    assert audio_file.encoder == ""
    assert audio_file.tracknumber == 0
    assert audio_file.tracktotal == 0
    assert audio_file.discnumber == 0
    assert audio_file.disctotal == 0


@pytest.mark.usefixtures("audio_file")
def test_trivial_tags(audio_file: Track):
    audio_file.clear_tags()
    audio_file.album = FakeTag.ALBUM.value
    audio_file.genre = FakeTag.GENRE.value
    audio_file.date = FakeTag.DATE.value
    audio_file.title = FakeTag.TITLE.value
    assert audio_file.album == FakeTag.ALBUM.value
    assert audio_file.genre == FakeTag.GENRE.value
    assert audio_file.date == FakeTag.DATE.value
    assert audio_file.title == FakeTag.TITLE.value
    audio_file.close()


@pytest.mark.parametrize(
    "artist,expected",
    [
        (FakeTag.ARTIST.value, [FakeTag.ARTIST.value]),
        ([FakeTag.ARTIST.value], [FakeTag.ARTIST.value]),
        (
            [FakeTag.ARTIST.value, FakeTag.ARTIST.value],
            [FakeTag.ARTIST.value, FakeTag.ARTIST.value],
        ),
    ],
)
@pytest.mark.usefixtures("audio_file")
def test_artist(audio_file: Track, artist: str | list[str], expected: list[str]):
    audio_file.artist = artist  # type: ignore
    assert audio_file.artist == expected
    audio_file.close()


@pytest.mark.usefixtures("audio_file")
def test_discnumber_disctotal(audio_file: Track):
    with pytest.raises(ValueError):
        audio_file.discnumber = 0
    with pytest.raises(ValueError):
        audio_file.disctotal = 0
    with pytest.raises(ValueError):
        audio_file.disctotal = 1
        audio_file.discnumber = 2
    audio_file.clear_tags()
    with pytest.raises(ValueError):
        audio_file.discnumber = 2
        audio_file.disctotal = 1
    audio_file.clear_tags()
    audio_file.disctotal = 2
    audio_file.discnumber = 2
    assert audio_file.disctotal == 2 and audio_file.discnumber == 2
    audio_file.close()


@pytest.mark.usefixtures("audio_file")
def test_tracknumber_tracktotal(audio_file: Track):
    with pytest.raises(ValueError):
        audio_file.tracknumber = 0
    with pytest.raises(ValueError):
        audio_file.tracktotal = 0
    with pytest.raises(ValueError):
        audio_file.tracktotal = 1
        audio_file.tracknumber = 2
    audio_file.clear_tags()
    with pytest.raises(ValueError):
        audio_file.tracknumber = 2
        audio_file.tracktotal = 1
    audio_file.clear_tags()
    audio_file.tracktotal = 2
    audio_file.tracknumber = 2
    assert audio_file.tracktotal == 2 and audio_file.tracknumber == 2
    audio_file.close()


@pytest.mark.usefixtures("audio_file")
def test_format_broken_pattern(audio_file: Track):
    audio_file.close()
    with pytest.raises(ValueError):
        audio_file.format_filename(pattern="NotAValidPattern")


@pytest.mark.usefixtures("audio_file")
def test_format_missing_tags(audio_file: Track):
    audio_file.clear_tags()
    with pytest.raises(ValueError):
        audio_file.format_filename()
    audio_file.close()


@pytest.mark.parametrize(
    "pattern,artists,disctotal,discnumber,tracktotal,expected",
    [
        (
            Pattern.SINGLE_DISC.value,
            [FakeTag.ARTIST.value],
            1,
            1,
            1,
            f"1 - {FakeTag.TITLE.value}",
        ),
        ("", [FakeTag.ARTIST.value], 1, 1, 1, f"1 - {FakeTag.TITLE.value}"),
        (
            Pattern.MULTI_DISC.value,
            [FakeTag.ARTIST.value],
            10,
            2,
            15,
            f"02-01 - {FakeTag.TITLE.value}",
        ),
        ("", [FakeTag.ARTIST.value], 10, 2, 15, f"02-01 - {FakeTag.TITLE.value}"),
        ("{N} - {A}", ["Some/Track"], 1, 1, 1, "1 - Some-Track"),
    ],
)
@pytest.mark.usefixtures("audio_file")
def test_format_filename(
    audio_file: Track,
    artists: list[str],
    pattern: str,
    disctotal: int,
    discnumber: int,
    tracktotal: int,
    expected: str,
):
    audio_file.artist = artists
    audio_file.disctotal = disctotal
    audio_file.discnumber = discnumber
    audio_file.tracktotal = tracktotal
    assert audio_file.format_filename(pattern) == expected
    audio_file.close()

from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
from pathlib import Path
import shutil
import sys
import pytest
from audiotag.track import Track

if TYPE_CHECKING:
    from typing import Union


class Files(Enum):
    value: str
    AUDIO = "noise.opus"
    IMAGE = "black.jpg"


class FakeTag(Enum):
    """Enum for fake tag values used in testing"""

    value: Union[str, int]
    ARTIST = "artist"
    ALBUM = "album"
    GENRE = "genre"
    DATE = 2000
    TITLE = "title"
    ENCODER = "Lavc58.134.100 libopus"
    TRACKNUMBER = 1
    TRACKTOTAL = 1
    DISCNUMBER = 1
    DISCTOTAL = 1


def _module_dir() -> Path:
    module_dir_str = sys.modules[__name__].__file__
    assert module_dir_str
    return Path(module_dir_str).parent


@pytest.fixture(scope="function", name="mixed_dir")
def fixture_mixed_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir_name = _module_dir()
    input_dir = Path(f"{dir_name}/testdata/")
    copy_dir = tmp_path_factory.mktemp("tmp-mixed")
    shutil.copyfile(src=input_dir / Files.AUDIO.value, dst=copy_dir / Files.AUDIO.value)
    shutil.copyfile(src=input_dir / Files.IMAGE.value, dst=copy_dir / Files.IMAGE.value)
    return copy_dir


@pytest.fixture(scope="function", name="image_dir")
def fixture_image_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir_name = _module_dir()
    image_file = Path(f"{dir_name}/testdata/{Files.IMAGE.value}")
    copy = tmp_path_factory.mktemp("tmp-image") / Files.IMAGE.value
    shutil.copyfile(src=image_file, dst=copy)
    return copy.parent


@pytest.fixture(scope="function", name="audio_file")
def fixture_audio_file(tmp_path_factory: pytest.TempPathFactory) -> Track:
    dir_name = _module_dir()
    opus_file = Path(f"{dir_name}/testdata/{Files.AUDIO.value}")
    copy = tmp_path_factory.mktemp("tmp-audio") / Files.AUDIO.value
    shutil.copyfile(src=opus_file, dst=copy)
    track = Track(copy)
    track.clear_tags()
    track.artist = FakeTag.ARTIST.value  # type: ignore
    track.album = FakeTag.ALBUM.value
    track.genre = FakeTag.GENRE.value
    track.title = FakeTag.TITLE.value
    track.date = FakeTag.DATE.value
    track.tracknumber = FakeTag.TRACKNUMBER.value
    track.tracktotal = FakeTag.TRACKTOTAL.value
    track.discnumber = FakeTag.DISCNUMBER.value
    track.disctotal = FakeTag.DISCTOTAL.value
    track.save()
    return track

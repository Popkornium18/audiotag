from __future__ import annotations
import functools
import math
from typing import TYPE_CHECKING
import taglib
from enum import Enum
from pathlib import Path

if TYPE_CHECKING:
    from typing import Optional, Any


class Tag(Enum):
    """Enum with common tag strings"""

    value: str
    ALBUM = "ALBUM"
    ARTIST = "ARTIST"
    DATE = "DATE"
    DISCNUMBER = "DISCNUMBER"
    DISCTOTAL = "DISCTOTAL"
    ENCODER = "ENCODER"
    GENRE = "GENRE"
    TITLE = "TITLE"
    TRACKNUMBER = "TRACKNUMBER"
    TRACKTOTAL = "TRACKTOTAL"


class Pattern(Enum):
    """Enum with default patterns for filenames"""

    SINGLE_DISC = "{N} - {T}"
    MULTI_DISC = "{D}-{N} - {T}"


@functools.total_ordering
class Track:

    _file: taglib.File
    path: Path

    def __init__(self, path: Path):
        self._file = taglib.File(str(path))
        self.path = path

    def __lt__(self, other: Track) -> bool:
        return self.path < other.path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Track):
            return NotImplemented
        return self.path == other.path

    def __repr__(self) -> str:
        return f"Track('{str(self.path)}')"

    @property
    def encoder(self) -> str:
        encoder = self._get_tag(Tag.ENCODER)
        return encoder[0] if encoder else ""

    @property
    def artist(self) -> list[str]:
        artist = self._get_tag(Tag.ARTIST)
        return artist if artist else [""]

    @artist.setter
    def artist(self, artist: list[str] | str) -> None:  # type: ignore
        if isinstance(artist, str):
            self._file.tags[Tag.ARTIST.value] = [artist]
        else:
            self._file.tags[Tag.ARTIST.value] = artist

    @property
    def date(self) -> int:
        date = self._get_tag(Tag.DATE)
        return int(date[0]) if date else 0

    @date.setter
    def date(self, date: int) -> None:
        self._file.tags[Tag.DATE.value] = [str(date)]

    @property
    def genre(self) -> str:
        genre = self._get_tag(Tag.GENRE)
        return genre[0] if genre else ""

    @genre.setter
    def genre(self, genre: str) -> None:
        self._file.tags[Tag.GENRE.value] = [genre]

    @property
    def album(self) -> str:
        album = self._get_tag(Tag.ALBUM)
        return album[0] if album else ""

    @album.setter
    def album(self, album: str) -> None:
        self._file.tags[Tag.ALBUM.value] = [album]

    @property
    def title(self) -> str:
        title = self._get_tag(Tag.TITLE)
        return title[0] if title else ""

    @title.setter
    def title(self, title: str) -> None:
        self._file.tags[Tag.TITLE.value] = [title]

    @property
    def tracknumber(self) -> int:
        tracknumber = self._get_tag(Tag.TRACKNUMBER)
        return int(tracknumber[0]) if tracknumber else 0

    @tracknumber.setter
    def tracknumber(self, tracknumber: int) -> None:
        if tracknumber < 1:
            raise ValueError(f"{Tag.TRACKNUMBER.value} must be positive")
        if self.has_tag(Tag.TRACKTOTAL) and tracknumber > self.tracktotal:
            raise ValueError(
                f"{Tag.TRACKNUMBER.value} must not be greater than {Tag.TRACKTOTAL.value}"
            )
        self._file.tags[Tag.TRACKNUMBER.value] = [str(tracknumber)]

    @property
    def tracktotal(self) -> int:
        tracktotal = self._get_tag(Tag.TRACKTOTAL)
        return int(tracktotal[0]) if tracktotal else 0

    @tracktotal.setter
    def tracktotal(self, tracktotal: int) -> None:
        if tracktotal < 1:
            raise ValueError(f"{Tag.TRACKTOTAL.value} must be positive")
        if self.has_tag(Tag.TRACKNUMBER) and tracktotal < self.tracknumber:
            raise ValueError(
                f"{Tag.TRACKTOTAL.value} must not be less than {Tag.TRACKNUMBER.value}"
            )
        self._file.tags[Tag.TRACKTOTAL.value] = [str(tracktotal)]

    @property
    def discnumber(self) -> int:
        discnumber = self._get_tag(Tag.DISCNUMBER)
        return int(discnumber[0]) if discnumber else 0

    @discnumber.setter
    def discnumber(self, discnumber: int) -> None:
        if discnumber < 1:
            raise ValueError(f"{Tag.DISCNUMBER.value} must be positive")
        if self.has_tag(Tag.DISCTOTAL) and discnumber > self.disctotal:
            raise ValueError(
                f"{Tag.DISCNUMBER.value} must not be greater than {Tag.DISCTOTAL.value}"
            )
        self._file.tags[Tag.DISCNUMBER.value] = [str(discnumber)]

    @property
    def disctotal(self) -> int:
        disctotal = self._get_tag(Tag.DISCTOTAL)
        return int(disctotal[0]) if disctotal else 0

    @disctotal.setter
    def disctotal(self, disctotal: int) -> None:
        if disctotal < 1:
            raise ValueError(f"{Tag.DISCTOTAL.value} must be positive")
        if self.has_tag(Tag.DISCNUMBER) and disctotal < self.discnumber:
            raise ValueError(
                f"{Tag.DISCTOTAL.value} must not be less than {Tag.DISCNUMBER.value}"
            )
        self._file.tags[Tag.DISCTOTAL.value] = [str(disctotal)]

    def _get_tag(self, tag: Tag) -> Optional[list[str]]:
        """
        Returns the given tag as a list of strings or None if the tag is missing
        """
        if not self.has_tag(tag):
            return None
        tag_val: list[str] = self._file.tags[tag.value]
        return tag_val

    def save(self) -> None:
        self._file.save()

    def close(self) -> None:
        self._file.close()

    def format_string(self) -> str:
        """Format a human readable string"""
        string = f"Filename: {str(self.path)}\n"
        for tag, value in self._file.tags.items():
            string += f"{tag}: {value[0] if len(value) == 1 else value}\n"
        return string

    def format_filename(self, pattern: Optional[str] = None) -> str:
        """Format a string according to the given format string"""
        missing_tags: list[Tag] = [
            tag
            for tag in {
                Tag.ARTIST,
                Tag.TITLE,
                Tag.ALBUM,
                Tag.DATE,
                Tag.GENRE,
                Tag.TRACKNUMBER,
                Tag.TRACKTOTAL,
                Tag.DISCNUMBER,
                Tag.DISCTOTAL,
            }
            if not self.has_tag(tag)
        ]
        if missing_tags:
            raise ValueError(
                f"The following tags are missing {[t.value for t in missing_tags]}"
            )

        if not pattern:
            pattern = (
                Pattern.SINGLE_DISC.value
                if self.disctotal <= 1
                else Pattern.MULTI_DISC.value
            )

        def replace_forbidden(text: str) -> str:
            return text.replace("/", "-")

        def pad(number: int, total: int) -> str:
            num_leading_zeros = int(math.log10(total)) + 1
            return str(number).zfill(num_leading_zeros)

        formatted_str = pattern.format_map(
            {
                "A": replace_forbidden("-".join(self.artist)),
                "T": replace_forbidden(self.title),
                "L": replace_forbidden(self.album),
                "Y": str(self.date),
                "G": replace_forbidden(self.genre),
                "N": pad(number=self.tracknumber, total=self.tracktotal),
                "D": pad(number=self.discnumber, total=self.disctotal),
                "NO": str(self.tracktotal),
                "DO": str(self.disctotal),
            }
        )
        if formatted_str == pattern:
            raise ValueError(f"Check if pattern '{pattern}' is correct")
        return formatted_str

    def set_tags(self, tags: dict[Tag, str | int]) -> bool | Any:
        """Set the new tags from the given dictionary and return if the tags have changed"""
        old_tags = self._file.tags.copy()
        for tag, value in tags.items():
            value_str = str(value) if isinstance(value, int) else value
            self._file.tags[tag.value] = [value_str]
        return not self._file.tags == old_tags

    def remove_tags(self, tags: set[Tag]) -> bool | Any:
        """Remove the given Tags and return if the taglist was actually modified"""
        old_tags = self._file.tags.copy()
        for tag in tags:
            self._file.tags.pop(tag.value)
        return not self._file.tags == old_tags

    def has_tag(self, tag: Tag) -> bool:
        """Returns whether a tag is set"""
        return tag.value in self._file.tags

    def clear_tags(self, keep: Optional[set[Tag]] = None) -> None:
        """
        Remove all tags other than the ones listed in 'keep' which defaults
        to ENCODER.
        """
        keep = {Tag.ENCODER} if keep is None else keep
        self._file.tags = {
            tag.value: self._file.tags[tag.value]
            for tag in keep
            if tag.value in self._file.tags
        }

    def copy_tags(self, source: Track, omit_tags: Optional[set[Tag]] = None) -> None:
        """
        Copy the tags from the given Track to this one. Tags in omit_tags are
        not copied. omit_tags defaults to ENCODER.
        """
        omit_tags = {Tag.ENCODER} if omit_tags is None else omit_tags
        omit_tags_str = {tag.value for tag in omit_tags}
        new_tags = {
            key: value
            for (key, value) in source._file.tags.items()
            if key not in omit_tags_str
        }

        for tag in omit_tags:
            value = self._get_tag(tag)
            if value:
                new_tags[tag.value] = value
        self._file.tags = new_tags

from __future__ import annotations
import functools
import math
from typing import TYPE_CHECKING
from enum import Enum
from pathlib import Path
import taglib
from prompt_toolkit.formatted_text import html
from audiotag import config

if TYPE_CHECKING:
    from typing import Optional, Any

VALUE_SEP = 2 * config.value_sep


class TagListInvalidException(Exception):
    def __init__(self, index: int, input: str):
        self.index = index
        self.input = input

    def __str__(self):
        return f"Value {self.index+1} in '{self.input}' is invalid"


class Tag(Enum):
    """Enum with common tag strings"""

    value: str
    ALBUM = "ALBUM"
    ALBUMARTIST = "ALBUMARTIST"
    ARTIST = "ARTIST"
    DATE = "DATE"
    DISCNUMBER = "DISCNUMBER"
    DISCTOTAL = "DISCTOTAL"
    ENCODER = "ENCODER"
    GENRE = "GENRE"
    TITLE = "TITLE"
    TRACKNUMBER = "TRACKNUMBER"
    TRACKTOTAL = "TRACKTOTAL"


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

    @staticmethod
    def split_tag(input_text: str) -> list[Any]:
        """Splits a string that contains a separator into a list"""
        input_list = input_text.split(VALUE_SEP)
        value_sep_half = list(VALUE_SEP)[0]
        input_split = [
            v.replace(f"\\{value_sep_half}", value_sep_half) for v in input_list
        ]

        for i, value in enumerate(input_split):
            if not value:
                raise TagListInvalidException(index=i, input=input_text)
        return input_split

    @property
    def encoder(self) -> str:
        encoder = self._get_tag(Tag.ENCODER)
        return encoder[0] if encoder else ""

    @property
    def artist(self) -> list[str]:
        artist = self._get_tag(Tag.ARTIST)
        return artist if artist else [""]

    @artist.setter
    def artist(self, artist: list[str]) -> None:
        self._file.tags[Tag.ARTIST.value] = artist

    @property
    def album_artist(self) -> list[str]:
        albumartist = self._get_tag(Tag.ALBUMARTIST)
        return albumartist if albumartist else [""]

    @album_artist.setter
    def album_artist(self, album_artist: list[str]) -> None:
        self._file.tags[Tag.ALBUMARTIST.value] = album_artist

    @property
    def date(self) -> int:
        date = self._get_tag(Tag.DATE)
        try:
            return int(date[0]) if date else 0
        except ValueError:
            return 0

    @date.setter
    def date(self, date: int) -> None:
        self._file.tags[Tag.DATE.value] = [str(date)]

    @property
    def genre(self) -> list[str]:
        genre = self._get_tag(Tag.GENRE)
        return genre if genre else [""]

    @genre.setter
    def genre(self, genre: list[str]) -> None:
        self._file.tags[Tag.GENRE.value] = genre

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
        try:
            return int(tracknumber[0]) if tracknumber else 0
        except ValueError:
            return 0

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
        try:
            return int(tracktotal[0]) if tracktotal else 0
        except ValueError:
            return 0

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

    def tags_string(self) -> str:
        """Format tags as a human readable string"""
        string = f"Filename: {str(self.path)}\n"
        for tag, value in self._file.tags.items():
            string += f"{tag}: {', '.join([f'{v}' for v in value])}\n"
        return string

    def tags_html(self) -> html.HTML:
        """Format tags as a HTML string. The content is the same as Track.tags_string()"""
        path_escaped = html.html_escape(str(self.path))
        string = f"<tag>Filename</tag>: <path>{path_escaped}</path>\n"
        for tag, value in self._file.tags.items():
            value_escaped = [html.html_escape(v) for v in value]
            value_format = (
                ", ".join(
                    [f"<valuemultiple>{v}</valuemultiple>" for v in value_escaped]
                )
                if len(value) > 1
                else value_escaped[0]
            )
            string += f"<tag>{tag}</tag>: {value_format}\n"
        return html.HTML(string)

    def format_tags(self, as_html: bool) -> str | html.HTML:
        """Format tags as HTML or str"""
        return self.tags_html() if as_html else self.tags_string()

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
                config.pattern_single_disc
                if self.disctotal <= 1
                else config.pattern_multi_disc
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
                "G": replace_forbidden("-".join(self.genre)),
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
            if isinstance(value, int):
                self._file.tags[tag.value] = [str(value)]
            elif tag in [Tag.ARTIST, Tag.ALBUMARTIST, Tag.GENRE]:
                value_list: list[str] = Track.split_tag(value)
                self._file.tags[tag.value] = value_list
            else:
                self._file.tags[tag.value] = [value]
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

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
from prompt_toolkit.formatted_text import html
from prompt_toolkit.formatted_text.base import FormattedText, to_formatted_text
from prompt_toolkit.application.current import get_app
from prompt_toolkit.shortcuts.prompt import prompt
from prompt_toolkit.shortcuts.utils import print_formatted_text
from prompt_toolkit.validation import ValidationError, Validator
from audiotag import styles
import audiotag.config as config
from audiotag.track import TagListInvalidException, Track, VALUE_SEP

if TYPE_CHECKING:
    pass


class NoSuchDirectoryError(Exception):
    pass


class NoAudioFilesFoundError(Exception):
    pass


def formatted_text_from_str(text: str) -> FormattedText:
    """
    Creates FormattedText from a string containing HTML tags
    """
    return to_formatted_text(html.HTML(text))


def get_toolbar_text():
    text = get_app().current_buffer.text
    if VALUE_SEP not in text:
        return html.HTML(
            f"<b>Hint</b>: Use '<i>{VALUE_SEP}</i>' to input multiple values"
        )
    else:
        values = text.split(VALUE_SEP)
        values_escaped = [
            html.html_escape(v.replace(f"\\{VALUE_SEP}", VALUE_SEP)) for v in values
        ]
        return formatted_text_from_str(
            f"<b>Values</b>: <u>{'</u>, <u>'.join(values_escaped)}</u>"
        )


def _validate_non_empty(text: str):
    if not text:
        raise ValidationError(message="Input must not be empty", cursor_position=0)


class NonEmptyValidator(Validator):
    def validate(self, document):
        text: str = document.text
        _validate_non_empty(text)


class ListValidator(Validator):
    def validate(self, document):
        text: str = document.text
        _validate_non_empty(text)
        if VALUE_SEP in text:
            try:
                Track.split_tag(text)
            except TagListInvalidException as e:
                raise ValidationError(message=str(e), cursor_position=0)


class YesNoValidator(Validator):
    def validate(self, document):
        text: str = document.text
        _validate_non_empty(text)

        if text.lower() not in ["y", "n"]:
            raise ValidationError(
                message="Answer must be 'y' or 'n'", cursor_position=1
            )


class NumberValidator(Validator):
    def validate(self, document):
        text: str = document.text
        _validate_non_empty(text)

        if text and not text.isdigit():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message="Input must be a number", cursor_position=i)


def yes_no(question: str) -> bool:
    """
    Continuously asks a yes/no question until user input is in [yYnN].
    Returns True or False respectively.
    """

    answer = prompt(
        editing_mode=config.editing_mode,
        message=question,
        default="y",
        validator=YesNoValidator(),
    )
    return answer.lower() == "y"


def strings_to_paths(strings: list[str]) -> list[Path]:
    """Converts a list of filenames in string form into a list of paths"""
    return [Path(string) for string in strings]


def open_tracks(paths: list[Path]) -> list[Track]:
    """
    Opens all files in the param filenames with taglib.
    Raises NoAudioFilesFoundError if no files can be opened.
    """
    tracks: list[Track] = []
    for path in paths:
        try:
            track = Track(path)
        except OSError:
            print(f"Unable to open file '{str(path)}'")
            continue
        tracks.append(track)
    if not tracks:
        raise NoAudioFilesFoundError("No files could be opened")
    return tracks


def list_files(directory: Path) -> list[Path]:
    """
    Returns a list of all the files in a given directory.
    Raises DirectoryEmptyError if directory does not exist.
    """
    if not directory.exists() or directory.is_file():
        raise NoSuchDirectoryError(f"Directory '{directory}' does not exist.")

    children = [child for child in directory.iterdir() if child.is_file()]
    return children


def print_to_console(text: str | html.HTML) -> None:
    """
    Prints the given text as styled if it is HTML or plain text if it is a str
    """
    if isinstance(text, html.HTML):
        print_formatted_text(to_formatted_text(text), style=styles.style_track)
    elif isinstance(text, str):
        print(text)
    else:
        raise ValueError(f"Expected str or HTML, got {type(text)}")

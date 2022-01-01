from __future__ import annotations

version: str

class File:
    """
    Class representing an audio file with metadata ("tags").

        To read tags from an audio file, create a *File* object, passing the file's path to the
        constructor (should be a unicode string):

        >>> f = taglib.File('/path/to/file.ogg')

        The tags are stored in the attribute *tags* as a *dict* mapping strings (tag names)
        to lists of strings (tag values).

        >>> for tag, values in f:
        >>>     print('{}->{}'.format(tag, ', '.join(values)))

        If the file contains some metadata that is not supported by pytaglib or not representable
        as strings (e.g. cover art, proprietary data written by some programs, ...), according
        identifiers will be placed into the *unsupported* attribute of the File object. Using the
        method *removeUnsupportedProperties*, some or all of those can be removed.

        Additionally, the readonly attributes *length*, *bitrate*, *sampleRate*, and *channels* are
        available with their obvious meanings.

        >>> print('File length: {}'.format(f.length))

        Changes to the *tags* attribute are stored using the *save* method.

        >>> f.save()
    """

    bitrate: int
    channels: int
    length: int
    path: str
    readOnly: bool
    sampleRate: int
    tags: dict[str, list[str]]
    unsupported: list[str]
    def close(self) -> None:
        """
        Closes the file by deleting the underlying Taglib::File object. This will close any open
        streams. Calling methods like `save()` or the read-only properties after `close()` will
        raise an exception.
        """
        pass
    def removeUnsupportedProperties(self, properties: list[str]) -> None:
        """This is a direct binding for the corresponding TagLib method."""
        pass
    def save(self) -> dict[str, list[str]]:
        """
        Store the tags currently hold in the `tags` attribute into the file.

        If some tags cannot be stored because the underlying metadata format does not support them,
        the unsuccesful tags are returned as a "sub-dictionary" of `self.tags` which will be empty
        if everything is ok.

        Raises
        ------
        OSError
            If the save operation fails completely (file does not exist, insufficient rights, ...).
        ValueError
            When attempting to save after the file was closed.
        """
        pass
    def __init__(self, path: str):
        pass
    def __repr__(self):
        """Return repr(self)."""
        pass

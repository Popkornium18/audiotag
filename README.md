# pytagger

Pytagger is a command line audio tagger written in python3. It uses [TagLib](http://taglib.org/) to write the metadata. It features a very simple to use interactive mode which lets you tag a single album as fast as possible.

## Installation

You can install pytagger directly from PyPI

```
pip install pytagger
```

## Usage

Pytagger offers different subcommands:

```
Usage:
  pytagger interactive <FILE>...
  pytagger print <FILE>...
  pytagger clean <FILE>...
  pytagger rename [-p PATTERN] <FILE>...
```

The `print` subcommand prints all tags. Multiple values per tag will be printed as a list.

```
$ pytagger print *.flac
Filename: /path/to/files/1 - At Giza.flac
ALBUM: ['Conference of the Birds']
ARTIST: ['Om']
DATE: ['2006']
DISCNUMBER: ['1']
DISCTOTAL: ['1']
ENCODER: ['Lavf58.12.100']
GENRE: ['Doom Metal']
TITLE: ['At Giza']
TRACKNUMBER: ['1']
TRACKTOTAL: ['2']

Filename: /path/to/files/2 - Flight of the Eagle.flac
ALBUM: ['Conference of the Birds']
ARTIST: ['Om']
DATE: ['2006']
DISCNUMBER: ['1']
DISCTOTAL: ['1']
ENCODER: ['Lavf58.12.100']
GENRE: ['Doom Metal']
TITLE: ['Flight of the Eagle']
TRACKNUMBER: ['2']
TRACKTOTAL: ['2']
```

The `interactive` subcommand interprets all given files as a single album and asks for all the necessary information. If the `Number of discs` value is anything greater than 1, pytagger will ask you which disk you are currently tagging. Otherwise the `DISCNUMBER` tag will also be set to 1. `Number of songs` is used to determine the number of leading zeroes when you use the `rename` subcommand.

```
$ pytagger interactive *.flac
Artist: Om
Albumtitle: Conference of the Birds
Genre: Doom Metal
Year: 2006
Number of songs: 2
Number of discs: 1
/path/to/files/1 - At Giza.flac
Title: At Giza
/path/to/files/2 - Flight of the Eagle.flac
Title: Flight of the Eagle

```

The `rename` subcommand lets you rename files based on the audio tags. You have to provide a pattern for renaming. The pattern may contain a combination of these placeholders:

* **{L}**: Album
* **{R}**: Artist
* **{G}**: Genre
* **{T}**: Title
* **{N}**: Track
* **{D}**: Discnumber
* **{Y}**: Year

You do _not_ have to add the extension to the pattern. Pytagger adds the extension to the output file name for you.

```
$ ls
01-at_giza.flac  02-flight_of_the_eagle.flac

$ pytagger rename -p "{N} - {T}" *.flac

$ ls
'1 - At Giza.flac'  '2 - Flight of the Eagle.flac'

```

The `clean` subcommand removes all tags from the file _except_ the `ENCODER` tag.

## Dependencies

The following dependencies are needed to run pytagger:

* [docopt](https://pypi.org/project/docopt/): For parsing command line arguments
* [pytaglib](https://pypi.org/project/pytaglib/): Python wrapper for accessing TagLib

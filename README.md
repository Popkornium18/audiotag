# audiotag
[![Tests](https://github.com/Popkornium18/audiotag/actions/workflows/tests.yml/badge.svg)](https://github.com/Popkornium18/audiotag/actions/workflows/tests.yml)
[![CodeQL](https://github.com/Popkornium18/audiotag/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Popkornium18/audiotag/actions/workflows/codeql-analysis.yml)
[![PyPI](https://github.com/Popkornium18/audiotag/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Popkornium18/audiotag/actions/workflows/python-publish.yml)

Audiotag is a command line audio tagger written in python3.
It uses [TagLib](http://taglib.org/) to write the metadata.
It features a very simple to use interactive mode which lets you tag a single album as fast as possible.

## Installation

You can install audiotag directly from PyPI.

```
pip install audiotag
```

If you are running **Arch Linux** you can install it from the **AUR**. The package is called [`audiotag`](https://aur.archlinux.org/packages/audiotag/).

## Usage

Audiotags functionality is split into different subcommands.

```
usage: audiotag [-h] [-v] {clean,copy,interactive,print,rename,set} ...

positional arguments:
  {clean,copy,interactive,print,rename,set}
    clean               delete all tags except 'ENCODER'
    copy                copy the tags from files in one folder to those in another folder
    interactive         tag a single album interactively. Treats files in subdirectories as different discs.
    print               print all tags
    rename              rename files based on their tags
    set                 set or delete tags

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

### Print

The `print` subcommand prints all tags.
Multiple values per tag will be printed as a list.

```
$ audiotag print *.flac
Filename: /path/to/files/1 - At Giza.flac
ALBUM: 'Conference of the Birds'
ARTIST: 'Om'
DATE: '2006'
DISCNUMBER: '1'
DISCTOTAL: '1'
ENCODER: 'Lavf58.12.100'
GENRE: 'Doom Metal'
TITLE: 'At Giza'
TRACKNUMBER: '1'
TRACKTOTAL: '2'

Filename: /path/to/files/2 - Flight of the Eagle.flac
ALBUM: 'Conference of the Birds'
ARTIST: 'Om'
DATE: '2006'
DISCNUMBER: '1'
DISCTOTAL: '1'
ENCODER: 'Lavf58.12.100'
GENRE: 'Doom Metal'
TITLE: 'Flight of the Eagle'
TRACKNUMBER: '2'
TRACKTOTAL: '2'
```

### Interactive

The `interactive` subcommand interprets all given files as a single album and asks for all the necessary information.
If the the files are in different directories, audiotag assumes that each directory is a disk of a multi-disc release.
The `TRACKTOTAL` and `DISCTOTAL` tags are set automatically.

```
$ audiotag interactive *.flac
Artist: Om
Albumtitle: Conference of the Birds
Genre: Doom Metal
Year: 2006
1 - At Giza.flac
Title 1: At Giza
2 - Flight of the Eagle.flac
Title 2: Flight of the Eagle
```

### Set

If you want to set the tags in a non-interactive way you can use the `set` command.
You can choose from these options:

*  `--artist="Example"`
*  `--title="Example"`
*  `--album="Example"`
*  `--date=2000`
*  `--genre="Example"`
*  `--tracknumber=1`
*  `--discnumber=2`
*  `--tracktotal=10`
*  `--disctotal=2`

If you want to remove tags you can choose these options:

*  `--noartist`
*  `--notitle`
*  `--noalbum`
*  `--nodate`
*  `--nogenre`
*  `--notracknumber`
*  `--nodiscnumber`
*  `--notracktotal`
*  `--nodisctotal`

You can combine these options as you like.
Here is an example:

```
$ audiotag set --artist=Om --album="Conference of the Birds" --nodiscnumber 01-at_giza.flac
```

### Clean

The `clean` subcommand removes all tags from the given files.
If you want to keep certain tags, you can specify them using the `--keep` parameter.
If none are specified, audiotag defaults to keeping the `ENCODER` tag.

### Rename

The `rename` subcommand lets you rename files based on the audio tags.
You have to provide a pattern for renaming.
The pattern may contain a combination of these placeholders:

* **{A}**:  Artist
* **{T}**:  Title
* **{L}**:  Album
* **{Y}**:  Date
* **{G}**:  Genre
* **{N}**:  Tracknumber
* **{D}**:  Discnumber
* **{NT}**:  Tracktotal
* **{DT}**:  Disctotal

If you don't specify a pattern, audiotag will use `{N} - {T}` if the _Disctotal_ tag is set to `1` or `{D}-{N} - {T}` if the _Disctotal_ tag is set to something else or missing.
You do _not_ have to add the extension to the pattern.
Audiotag adds the extension to the output file name for you.

```
$ ls
01-at_giza.flac  02-flight_of_the_eagle.flac

$ audiotag rename *.flac

$ ls
'1 - At Giza.flac'  '2 - Flight of the Eagle.flac'
```

If the new filename already exists Audiotag will ask if you want to overwrite the existing file. This check can be disabled with the `-f` or `--force` option.

### Copy
The `copy` subcommand copies the tags from all the files in the sourcefolder to corresponding files in the destination folder.
The filenames are sorted alphabetically before they are matched.
Note that the `ENCODER` tag ist _not_ copied.

## Dependencies

The following dependencies are needed to run audiotag:
* [pytaglib](https://pypi.org/project/pytaglib/): Python wrapper for accessing TagLib

Optional dependencies are:
* [gnureadline](https://pypi.org/project/gnureadline/): For better user input (Readline should already be installed on any Linux system)

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
Filename: 1 - Nova.flac
ALBUM: Nova/Moth
ALBUMARTIST: Burial & Four Tet
ARTIST: Burial, Four Tet
DATE: 2022
DISCNUMBER: 1
DISCTOTAL: 1
ENCODER: Lavf58.76.100
GENRE: Electronic, UK Garage, Future Garage
TITLE: Nova
TRACKNUMBER: 1
TRACKTOTAL: 2

Filename: 2 - Moth.flac
ALBUM: Nova/Moth
ALBUMARTIST: Burial & Four Tet
ARTIST: Burial, Four Tet
DATE: 2022
DISCNUMBER: 1
DISCTOTAL: 1
ENCODER: Lavf58.76.100
GENRE: Electronic, UK Garage, Future Garage
TITLE: Moth
TRACKNUMBER: 2
TRACKTOTAL: 2
```

### Interactive

The `interactive` subcommand interprets all given files as a single album and asks for all the necessary information.
If the the files are in different directories, audiotag assumes that each directory is a disk of a multi-disc release.
The `TRACKTOTAL` and `DISCTOTAL` tags are set automatically.
Multiple values have to be seperated by `//`.

```
$ audiotag interactive *.flac
Artist: Burial//Four Tet
Album Artist: Burial & Four Tet
Albumtitle: Nova/Moth
Genre: Electronic//UK Garage//Future Garage
Year: 2022
File: 1 - Nova.flac
Track 1: Nova
File: 2 - Moth.flac
Track 2: Moth
```

If you pass the `--compilation` flag, audiotag will ask the artist of each track.

### Set

If you want to set the tags in a non-interactive way you can use the `set` command.
You can choose from these options:

*  `--artist="Example"`
*  `--albumartist="Example"`
*  `--title="Example"`
*  `--album="Example"`
*  `--date=2000`
*  `--genre="Example"`
*  `--tracknumber=1`
*  `--discnumber=2`
*  `--tracktotal=10`
*  `--disctotal=2`

Multiple artists and genres have to be separated by `//`.
If you want to add a literal `//` you have to escape it like this `\/\/`.

If you want to remove tags you can choose these options:

*  `--noartist`
*  `--noalbumartist`
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
$ audiotag set --artist="Burial & Four Tet" --album="Nova/Moth" --nodiscnumber 01-nova.flac
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
01-nova.flac  02-moth.flac

$ audiotag rename *.flac

$ ls
'1 - Nova.flac'  '2 - Moth.flac'
```

If the new filename already exists Audiotag will ask if you want to overwrite the existing file. This check can be disabled with the `-f` or `--force` option.

### Copy
The `copy` subcommand copies the tags from all the files in the sourcefolder to corresponding files in the destination folder.
The filenames are sorted alphabetically before they are matched.
You may also specify a _single_ file as source and destination.
Note that the `ENCODER` tag ist _not_ copied.

## Dependencies

The following dependencies are needed to run audiotag:
* [pytaglib](https://pypi.org/project/pytaglib/): Python wrapper for accessing TagLib
* [prompt-toolkit](https://pypi.org/project/prompt-toolkit/): Better console I/O

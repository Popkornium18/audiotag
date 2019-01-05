# audiotag

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

Audiotag offers different subcommands:

```
Usage:
  audiotag print FILE...
  audiotag interactive FILE...
  audiotag set [--artist=ARTIST|--noartist] [--title=TITLE|--notitle]
               [--album=ALBUM|--noalbum] [--date=DATE|--nodate]
               [--genre=GENRE|--nogenre]
               [--tracknumber=TRACKNUMBER|--notracknumber]
               [--tracktotal=TRACKTOTAL|--notracktotal]
               [--discnumber=DISCNUMBER|--nodiscnumber]
               [--disctotal=DISCTOTAL|--nodisctotal] FILE...
  audiotag clean FILE...
  audiotag rename [--pattern=PATTERN] [-f] FILE...
  audiotag -h | --help
  audiotag -v | --version
```

### Print

The `print` subcommand prints all tags.
Multiple values per tag will be printed as a list.

```
$ audiotag print *.flac
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

### Interactive

The `interactive` subcommand interprets all given files as a single album and asks for all the necessary information.
If the `Number of discs` value is anything greater than 1, audiotag will ask you which disk you are currently tagging.
Otherwise the `DISCNUMBER` tag will also be set to 1.
`Number of songs` is used to determine the number of leading zeros when you use the `rename` subcommand.

```
$ audiotag interactive *.flac
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

The `clean` subcommand removes all tags from the file _except_ the `ENCODER` tag.

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

## Dependencies

The following dependencies are needed to run audiotag:

* [docopt](https://pypi.org/project/docopt/): For parsing command line arguments
* [pytaglib](https://pypi.org/project/pytaglib/): Python wrapper for accessing TagLib

Optional dependencies are:
* [gnureadline](https://pypi.org/project/gnureadline/): For better user input (Readline should already be installed on any Linux system)

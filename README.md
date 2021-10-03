# Nicole - Lyrics Scraper
**N**ew-**I**ntrepid-**C**hief-**O**f-**L**yrics-**E**mbedders (obviously)

## Overview
Nicole is a program that searches for lyrics and writes them into the mp3-tag. 

Unfortunately, there needs to be a 5 second delay between each request to azlyrics.com because the site will block your ip for a while if you send many requests.

### Files
Nicole supports FLAC and mp3 files. Other files can not be edited (as of now).
Files that do not have a .flac or .mp3 extension are skipped automatically.
- mp3: lyrics are stored in "USLT" tag as "lyrics-   "
- flac: lyrics are stored as vorbis-comment with key "LYRICS"

### History
Nicole creates a history of all files that were processed in `~/.configs/nicole`.
If a file is in the history, it will be skipped unless `ignore_history=True`.
If the lyrics for a file can not be obtained, it is added to `~/.configs/nicole/failed_files`.
Those files are not skipped, the file only exists so that you can see which lyrics were not downloaded.

If you dont want your files in the history, add the `-n` option.

### azlyrics
Nicole creates an azlyrics.com url from the "title" and "artist" tags of the file.
The lyrics are extracted from the html document using regex.


## Usage
Command line options:
- `-d [directory]` process directory [directory]
- `-f [file]` process file [file]
- `-r` go through directories recursively
- `-s` silent, no command-line output
- `-i` ignore history
- `-n` do not write to history
- `-o` overwrite if the file already a lyrics
- `-t` test, do not write lyrics to file, but print to console

- `-h` show this
- `--rm_explicit` remove the "[Explicit]" lyrics warning from the song's title tag

If you do not specify a directory or file, the program will ask you if you want to use the current working directory.

## Installation
Clone this repository and install it using python-pip.
pip should also install https://github.com/seebye/mutagen, which is needed to read and write the mp3-tags.
```shell
cd ~/Downloads
git clone https://github.com/MatthiasQuintern/nicole.git
cd nicole
python3 -m pip install .
```
You can also install it system-wide using `sudo python3 -m pip install.`

After installing, you can use it like this: `nicole -ior -d ~/music/artist --rm_explicit`

## Changelog
### 1.1
- Lyrics are now properly encoded.
- If a title contains paranthesis or umlaute, multiple possible urls will be checked.

## Importand Notice
This software comes with no warranty!

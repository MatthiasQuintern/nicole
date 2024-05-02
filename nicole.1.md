% NICOLE(1) nicole 2.1.0
% Matthias Quintern
% May 2024

# NAME
**N**ew-**I**ntrepid-**C**hief-**O**f-**L**yrics-**E**mbedders (obviously)

Nicole is a program that searches for lyrics and writes them into the mp3-tag of a file.

# SYNOPSIS
| Directory:
|    **nicole** [OPTION...] -d DIRECTORY
| File:
|    **nicole** [OPTION...] -f FILE

## Files
Nicole supports FLAC and mp3 files. Other files can not be edited (as of now).
Files that do not have a .flac or .mp3 extension are skipped automatically.

**mp3**: lyrics are stored in "USLT" tag as "lyrics-   "

**flac**: lyrics are stored as vorbis-comment with key "LYRICS"

## History
Nicole creates a history of all files that were processed in `~/.configs/nicole`.
If a file is in the history, it will be skipped (unless `-i` is passed).
If the lyrics for a file can not be obtained, it is added to `~/.configs/nicole/failed_files`.
Those files are not skipped, the file only exists so that you can see which lyrics were not downloaded.

If you don't want your files in the history, add the `-n` option.

## genius
Nicole searches for lyrics using the genius api with the "title" and "artist" tags of the file.
If the title and artist names from genius are similar enough to the ones of the file,
the lyrics are scraped from the url obtained through the api.

## azlyrics
Nicole creates an azlyrics.com url from the "title" and "artist" tags of the file.
The lyrics are extracted from the html document using regex.

Unfortunately, there needs to be a 5 second delay between each request to azlyrics.com because 
the site will block your ip for a while if you send many requests.


# USAGE

## Command line options
**--directory**, **-d** directory
: process directory [directory]

**--file**, **-f** file
: process file [file]

**--recursive**, **-r**
: go through directories recursively

**--silent**
: silent, no command-line output

**--ignore-history**, **-i**
: ignore history

**--no-history**, **-n**
: do not write to history

**--overwrite**, **-o**
: overwrite if the file already has lyrics

**--test**, **-t**
: test, do not write lyrics to file, but print to stdout

**--rm-explicit**
: remove the "[Explicit]" lyrics warning from the song's title tag

**--site**, **-s** site
: onlysearch [site] for lyrics (genius or azlyrics)

One of `--file` and `--directory` must be given at least once.
Example: `nicole -ior -d ~/music/artist --rm-explicit`

# INSTALLATION AND UPDATING
To update nicole, simply follow the installation instructions.

## pacman (Arch Linux)
Installing nicole using the Arch Build System also installs the man-page and a zsh completion script, if you have zsh installed.
```shell
git clone https://github.com/MatthiasQuintern/nicole.git
cd nicole
makepkg -si
```

## pip
You can also install nicole with python-pip:
```shell
git clone https://github.com/MatthiasQuintern/nicole.git
cd nicole
python3 -m pip install .
```
You can also install it system-wide using `sudo python3 -m pip install.`

If you also want to install the man-page and the zsh completion script:
```shell
sudo cp nicole.1.man /usr/share/man/man1/nicole.1
sudo gzip /usr/share/man/man1/nicole.1
sudo cp _nicole.compdef.zsh /usr/share/zsh/site-functions/_nicole
sudo chmod +x /usr/share/zsh/site-functions/_nicole
```

## Dependencies
- https://github.com/quodlibet/mutagen read and write mp3-tags
- https://www.crummy.com/software/BeautifulSoup deal with the html from genius

The dependencies will be automatically installed when using the either of the two installation options.

# CHANGELOG
## 2.1.0
- Refactoring:
    - use argparse
    - use pyproject.toml
- Ignore case when matching a genius result

## 2.0
- Nicole now supports lyrics from genius!
- Added man-page
- Added zsh-completion

## 1.1
- Lyrics are now properly encoded.
- If a title contains parenthesis or umlaute, multiple possible urls will be checked.
- Files are now processed in order

# COPYRIGHT
Copyright  ©  2024  Matthias  Quintern.  License GPLv3+: GNU GPL version 3 <https://gnu.org/licenses/gpl.html>.\
This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.

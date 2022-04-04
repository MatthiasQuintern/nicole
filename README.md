# Nicole - Lyrics Scraper
**N**ew-**I**ntrepid-**C**hief-**O**f-**L**yrics-**E**mbedders (obviously)

## Overview
Nicole is a program that searches for lyrics and writes them into the mp3-tag of a file.

### Files
Nicole supports FLAC and mp3 files. Other files can not be edited (as of now).
Files that do not have a .flac or .mp3 extension are skipped automatically.
- mp3: lyrics are stored in "USLT" tag as "lyrics-   "
- flac: lyrics are stored as vorbis-comment with key "LYRICS"

### History
Nicole creates a history of all files that were processed in `~/.configs/nicole`.
If a file is in the history, it will be skipped (unless `-i` is passed).
If the lyrics for a file can not be obtained, it is added to `~/.configs/nicole/failed_files`.
Those files are not skipped, the file only exists so that you can see which lyrics were not downloaded.

If you don't want your files in the history, add the `-n` option.

### genius
Nicole searches for lyrics using the genius api using the "title" and "artist" tags of the file.
If the title and artist names from genius and the tags are similar, the lyrics are scraped from the url obtained through the api.

### azlyrics
Nicole creates an azlyrics.com url from the "title" and "artist" tags of the file.
The lyrics are extracted from the html document using regex.

Unfortunately, there needs to be a 5 second delay between each request to azlyrics.com because the site will block your ip for a while if you send many requests.

### Important Note
Since the lyrics are extracted from html pages and not from an api, the lyrics sites might temporarily block your ip address if you send too many requests.
If that is the case, wait a few hours and try again.

## Usage

### Command line options
- `-d [directory]` process directory [directory]
- `-f [file]` process file [file]
- `-r` go through directories recursively
- `-s` silent, no command-line output
- `-i` ignore history
- `-n` do not write to history
- `-o` overwrite if the file already has lyrics
- `-t` test, do not write lyrics to file, but print to stdout
- `-h` show this
- `--rm_explicit` remove the "[Explicit]" lyrics warning from the song's title tag
- `--site [site]` only search [site] for lyrics (genius or azlyrics)

If you do not specify a directory or file, the program will ask you if you want to use the current working directory.
Example: `nicole -ior -d ~/music/artist --rm_explicit`

## Installation and Updating
To update nicole, simply follow the installation instructions.

### pacman (Arch Linux)
Installing nicole using the Arch Build System also installs the man-page and a zsh completion script if you are using zsh as default shell.
```shell
git clone https://github.com/MatthiasQuintern/nicole.git
cd nicole
makepkg -si
```

### pip
Clone this repository and install it using python-pip.
```shell
git clone https://github.com/MatthiasQuintern/nicole.git
cd nicole
python3 -m pip install .
```
You can also install it system-wide using `sudo python3 -m pip install.`

If you also want to install the man-page and the zsh completion script:
```shell
sudo cp nicole.1.man /usr/share/man/man1/nicole.1
sudo cp _nicole.compdef.zsh /usr/share/zsh/site-functions/_nicole
sudo chmod +x /usr/share/zsh/site-functions/_nicole
```

### Dependencies
- https://github.com/seebye/mutagen: read and write mp3-tags
- https://www.crummy.com/software/BeautifulSoup/: deal with the html from genius
The dependencies will be automatically installed when using the either of the two installation options.

## Changelog
### 2.0
- Nicole now supports lyrics from genius!

### 1.1
- Lyrics are now properly encoded.
- If a title contains parenthesis or umlaute, multiple possible urls will be checked.
- Files are now processed in order

# Copyright
Copyright  ©  2022  Matthias  Quintern.  License GPLv3+: GNU GPL version 3 <https://gnu.org/licenses/gpl.html>.\
This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.

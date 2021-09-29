from mutagen import easyid3, id3
import urllib.request as ur
from os import path, getcwd, listdir, mkdir
from time import sleep

from sys import argv

import re

"""
Der Name Nicole ist frei erfunden und hat keine Bedeutung.
Jeglicher Zusammenhang mit einer Website der DHL wird hiermit ausdrücklich ausgeschlossen.
"""


class Nicole:
    """
    Overview:
        Nicole is a program that searches for lyrics and writes them into the mp3-tag "USLT".
        There is a 5 second delay between each request to azlyrics.com because the site will block your ip if there are too many requests.
    History:
        Nicole can create a history of all files that were processed in ~/.configs/nicole.
        If a file is in the history, it will be skipped unless ignore_history=True.
        If the lyrics for a file can not be obtained, it is added to ~/.configs/nicole/failed_files.
        Those files are not skipped, the file only exists so that you can see which lyrics were not downloaded.
    azlyrics:
        Nicole creates a azlyrics url from the title and artist mp3-tags of the file.
        The lyrics are extracted from the html document using regex.
    """
    def __init__(self, test_run=False, silent=False, write_history=True, ignore_history=False, overwrite_tag=False, recursive=False):
        self.test_run = test_run
        self.silent = silent

        self.write_history = write_history
        self.ignore_history = ignore_history
        
        self.overwrite_tag = overwrite_tag
        self.recursive = recursive

        self.lyrics_site = "azlyrics"
        self.delay = 5  # enough delay so that azlyrics doesnt block the ip

        self.history = []
        self.failed = []  # All files that failed
        if not self.ignore_history:
            self._load_history()

    def __del__(self):
        if self.write_history:
            self._write_history()
        else:
            print("NO")

    def _load_history(self):
        config_path = path.expanduser("~") + "/.config/nicole/"
        # check config dir exists
        if not path.isdir(config_path):
            mkdir(config_path)

        history_file_path = config_path + "history"
        # if history file does not exist, dont open it
        if not path.isfile(history_file_path):
            return

        history_file = open(history_file_path, "r")
        self.history = history_file.read().split("\n")
        history_file.close()

    def _write_history(self):
        config_path = path.expanduser("~") + "/.config/nicole/"

        history_file = open(config_path + "history", "w")
        for file in self.history:
            history_file.write(file + "\n")
        history_file.close()

        failed_file = open(config_path + "failed", "w")
        for file in self.failed:
            failed_file.write(file + "\n")
        failed_file.close()
        
    def get_url_azlyrics(self, artist:str, title:str):
        """
        Create a azlyrics html from the artist and title
        """
        # convert to lower case
        artist = artist.casefold()
        title = title.casefold()

        # remove 'a' or 'the' from the artist
        if artist[0:1] == "a ":
            artist = artist[2:]
        elif artist[0:3] == "the ":
            artist = artist[4:]

        # remove spaces, from the title
        for c in [' ', '-', ',', '.', '\'', '/']:
            title = title.replace(c, '')

        # replace some stuff
        old = ['ä', 'ö', 'ü', '&']
        new = ['a', 'o', 'u', "and"]

        for i in range(len(old)):
            title = title.replace(old[i], new[i])

        return "https://azlyrics.com/lyrics/" + artist + '/' + title + ".html"

    def get_lyrics_azlyrics(self, url):
        """
        Extract the lyrics from the html
        """
        # visit the url
        html = None
        try:
            html = str(ur.urlopen(url).read())
        except Exception:
            # if not self.silent:
            #     print("✕ Error with url: ", url)
            return

        lyrics = None
        match = re.search(r"<!\-\- Usage of azlyrics.com content by any third\-party lyrics provider is prohibited by our licensing agreement. Sorry about that. \-\->.+?</div>", html)
        if match:
            lyrics = match.group()
            lyrics = lyrics.replace("<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->", "")
            lyrics = lyrics.replace("</div>", "")
            lyrics = lyrics.replace("\n", "")
            lyrics = lyrics.replace("\\n", "")
            lyrics = lyrics.replace("\\r", "")
            lyrics = lyrics.replace("\\", "")
            lyrics = lyrics.replace("<br>", "\n")
            # remove all html tags
            for tag in re.finditer(r"<.+>", lyrics):
                lyrics = lyrics.replace(tag.group(), "")
            for tag in re.finditer(r"</.+>", lyrics):
                lyrics = lyrics.replace(tag.group(), "")

        return lyrics

    def process_dir(self, directory):
        if not path.isabs(directory):
            directory = path.normpath(getcwd() + "/" + directory)
        if not path.isdir(directory):
            print(f"Invalid directory: '{directory}'")
            return 1
        if not self.silent:
            print("Processing directory: " + directory)


        for entry in listdir(directory):
            entry = path.normpath(directory + "/" + entry)

            if path.isfile(entry):
                extension = path.splitext(entry)[1]

                # if sound file with mp3 tags
                if extension in [".mp3", ".flac", ".wav"] and (self.ignore_history or entry not in self.history):
                    self.process_file(entry)


            elif path.isdir(entry) and self.recursive:
                self.process_dir(entry)

    def process_file(self, file):
        if not path.isabs(file):
            file = path.normpath(getcwd() + "/" + file)
        if not path.isfile(file):
            print(f"Invalid filename: '{file}'")
            return 1
        audio = easyid3.EasyID3(file)
        artist = audio["artist"][0]
        title = audio["title"][0]

        audio = id3.ID3(file)

        # print(audio.pprint())

        if self.lyrics_site == "azlyrics":
            url = self.get_url_azlyrics(artist, title)
            
            lyrics = self.get_lyrics_azlyrics(url)
            if lyrics:
                # lyrics.encode("UTF16", "backslashreplace")
                lyrics.encode()
                if self.test_run:
                    print(f"{artist} - {title}:\n{lyrics}\n\n")
                elif self.overwrite_tag or audio.getall("USLT") == []:
                    # write to tags
                    audio.add(id3.USLT(encoding=id3.Encoding.UTF8, lang="   ", text=lyrics))
                    audio.save(v2_version=4)
                    if not self.silent:
                        print(f"✓ Written text to {artist} - {title}")

                    # add to history
                    if self.write_history and file not in self.history:
                        self.history.append(file)
                else:
                    print(f"Already has lyrics: {artist} - {title}")

                sleep(self.delay) # azlyrics blocks requests if there is no delay
            else:
                # add to failed
                if self.write_history and file not in self.failed:
                    self.failed.append(file)

                if not self.silent:
                    print(f"✕ Could not get lyrics for {artist} - {title}")
                    pass


def main():
    helpstring = """
Command line options:
    -d [directory] process directory [directory]
    -f [file] process file [file]
    -r go through directories recursively
    -s silent, no command-line output
    -i ignore history
    -n do not write to history
    -o overwrite if the file already has a comment
    -h show this
"""
    args = []
    if len(argv) > 1:
        # iterate over argv list and extract the args
        i = 1
        while i < len(argv):
            arg = argv[i]
            if "--" in arg:
                args.append(arg.replace("--", ""))

            elif "-" in arg:
                # check if option with arg, if yes add tuple to args
                if len(argv) > i + 1 and "-" not in argv[i+1]:
                    args.append((arg.replace("-", ""), argv[i+1]))
                    i += 1
                else:
                    for c in arg.replace("-", ""):
                        args.append(c)
            else:
                print(f"Invalid or missing argument: '{arg}'")
                print(helpstring)
                return 1

            i += 1

    options = {
            "t": False,
            "s": False,
            "n": True,
            "i": False,
            "o": False,
            "r": False,
            "h": False,
            }

    directory = None
    file = None

    for arg in args:
        if type(arg) == tuple:
            if arg[0] == "d": directory = arg[1]
            elif arg[0] == "f": file = arg[1]

        elif arg in options.keys():
            # flip the bool associated with the char
            if options[arg] == False: options[arg] = True
            else: options[arg] = False
        
        else:
            print(f"Invalid argument: '{arg}'")
            print(helpstring)
            return 1

    # show help
    if options["h"]:
        print(helpstring)
        return 0
    
    # create nicole instance
    nicole = Nicole(test_run=options["t"], silent=options["s"], write_history=options["n"], ignore_history=options["i"], overwrite_tag=options["o"], recursive=options["r"])

    # start with file or directory
    if file:
        nicole.process_file(file)
    elif directory:
        nicole.process_dir(directory)
    else:
        use_wdir = input("No file or directory given. Use working directory? (y/n): ")
        if use_wdir in "yY":
            nicole.process_dir(getcwd())
        else:
            print(helpstring)


if __name__ == "__main__":
    main()

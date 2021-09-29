from mutagen import easyid3, id3, flac
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
    def __init__(self, test_run=False, silent=False, write_history=True, ignore_history=False, overwrite_tag=False, recursive=False, rm_explicit=False):
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

        self.rm_explicit = rm_explicit

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

        # remove anything in square bracketrs (eg [Explicit])
        for match in re.finditer(r"[.*]", title):
            title = title.replace(match.group(), "")

        # remove spaces, from the title
        for c in [' ', '-', ',', '.', '\'', '"', '°', '`', '´', '/', '!', '?', '#', '*']:
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
            sleep(self.delay) # azlyrics blocks requests if there is no delay
        except Exception:
            sleep(self.delay) # azlyrics blocks requests if there is no delay
            return (False, f"Could not access url: {url}")

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

            return (True, lyrics)
        return (False, f"Could not find lyrics in html: {url}")

    def process_dir(self, directory):
        if not path.isabs(directory):
            directory = path.normpath(getcwd() + "/" + directory)
        if not path.isdir(directory):
            print(f"\nInvalid directory: '{directory}'")
            return 1
        if not self.silent:
            print("\nProcessing directory: " + directory)


        for entry in listdir(directory):
            entry = path.normpath(directory + "/" + entry)

            if path.isfile(entry):
                extension = path.splitext(entry)[1]

                # if sound file with mp3 tags
                if extension in [".mp3", ".flac"]:
                    success, message = self.process_file(entry)

                    # add to history
                    if self.write_history:
                        if success and entry not in self.history:
                            self.history.append(entry)
                        elif not success:
                            self.failed.append(entry)

                    if not self.silent:
                        if success:
                            print(f"✓ {entry}") 
                        else:
                            print(f"✕ {entry}")
                        print("   " + message)


            elif path.isdir(entry) and self.recursive:
                self.process_dir(entry)

    def process_file(self, file):
        if not path.isabs(file):
            file = path.normpath(getcwd() + "/" + file)
        if not path.isfile(file):
            return (False, f"Invalid filename: '{file}'")
        
        if not self.ignore_history and file in self.history:
            return (False, f"Already processed by nicole.")

        audio = None
        artist = None
        title = None

        has_lyrics = False

        # mp3/id3
        if ".mp3" in file:
            try:
                audio = id3.ID3(file)

                artist = audio.getall("TPE1")
                title = audio.getall("TIT2")

                has_lyrics = not (audio.getall("USLT") == [])
            except id3.ID3NoHeaderError:
                return (False, f"No id3 header found.")
        # flac
        elif ".flac" in file:
            try:
                audio = flac.FLAC(file)

                artist = audio.get("ARTIST")
                title = audio.get("TITLE")

                has_lyrics = not (audio.get("LYRICS") == None)
            except flac.FLACNoHeaderError:
                return (False, f"No FLAC comment header found.")

        if artist:
            artist = str(artist[0])
        if title:
            title = str(title[0])

        # dont proceed when not overwrite and audio has tags
        if not self.overwrite_tag and has_lyrics:
            return (False, f"Already has lyrics")

        # dont proceed when invalid audio/artist/title
        if not (audio and artist and title):
            return (False, f"Could not get tags.")

        if self.rm_explicit:
            for word in ["[Explicit]", "[exlicit]"]:
                if word in title:
                    title = str(title).replace(word, "")
                    title = title.strip(" ")
                    if type(audio) == id3.ID3:
                        audio.setall("TIT2", [id3.TIT2(text=title)])
                        audio.save()
                        print(f"Removed '{word}' from the title.")
                    elif type(audio) == flac.FLAC:
                        audio["TITLE"] = title
                        audio.save()
                        print(f"Removed '{word}' from the title.")
        print(audio.pprint())


        # currently the only supported site
        if self.lyrics_site == "azlyrics":
            url = self.get_url_azlyrics(artist, title)
            
            success, lyrics = self.get_lyrics_azlyrics(url)
            if success:
                if self.test_run:
                    print(f"{artist} - {title}:\n{lyrics}\n\n")
                # write to tags
                else:
                    if type(audio) == id3.ID3:
                        audio.add(id3.USLT(encoding=id3.Encoding.UTF8, lang="   ", text=lyrics))
                        audio.save(v2_version=4)
                    elif type(audio) == flac.FLAC:
                        audio["LYRICS"] = lyrics
                        audio.save()
                    else:
                        return (False, f"Could not write lyrics.")

                    # add to history
                    if self.write_history and file not in self.history:
                        self.history.append(file)

                return (True, f"Written lyrics to {artist} - {title}")
            else:
                return (False, lyrics)  # lyrics is error message here

        return (False, "Failed for unknown reason.")


def main():
    helpstring = """Command line options:
    -d [directory]      process directory [directory]
    -f [file]           process file [file]
    -r                  go through directories recursively
    -s                  silent, no command-line output
    -i                  ignore history
    -n                  do not write to history
    -o                  overwrite if the file already has lyrics
    -h                  show this
    --rm_explicit       remove the "[Explicit]" lyrics warning from the songs title tag"""
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
                if len(argv) > i + 1 and argv[i+1][0] != "-":
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
            "rm_explicit": False,
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
    nicole = Nicole(test_run=options["t"], silent=options["s"], write_history=options["n"], ignore_history=options["i"], overwrite_tag=options["o"], recursive=options["r"], rm_explicit=options["rm_explicit"])

    # start with file or directory
    if file:
        success, message = nicole.process_file(file)
        if not nicole.silent:
            if success:
                print(f"✓ {file}") 
            else:
                print(f"✕ {file}")
            print("   " + message)
    elif directory:
        try:
            nicole.process_dir(directory)
        except KeyboardInterrupt:
            print("")
    else:
        use_wdir = input("No file or directory given. Use working directory? (y/n): ")
        if use_wdir in "yY":
            nicole.process_dir(getcwd())
        else:
            print(helpstring)


if __name__ == "__main__":
    main()

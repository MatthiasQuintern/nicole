#!/usr/bin/env python3
# Copyright © 2024 Matthias Quintern.
# This software comes with no warranty.
# This software is licensed under the GPL3

from mutagen import easyid3, id3, flac

import urllib.parse, urllib.request, urllib.error
import re
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from json import loads
import argparse

from os import path, getcwd, listdir, mkdir
from time import sleep
from sys import argv

version = "2.1.0"

# Der Name Nicole ist frei erfunden und hat keine Bedeutung.
# Jeglicher Zusammenhang mit einer Website der DHL wird hiermit ausdrücklich ausgeschlossen.

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
    genius:
        Nicole searches the song from the title and artist mp3-tags via the genius api.
    """
    allowed_extensions = [".mp3", ".flac"]

    def __init__(self, test_run=False, silent=False, write_history=True, ignore_history=False, overwrite_tag=False, recursive=False, rm_explicit=False, lyrics_site="all"):
        self.dry_run = test_run
        self.silent = silent

        self.write_history = write_history
        self.ignore_history = ignore_history

        self.overwrite_tag = overwrite_tag
        self.recursive = recursive

        self.lyrics_site = lyrics_site
        self.delay = 5  # enough delay so that azlyrics doesnt block the ip

        self.genius_search = "https://api.genius.com/search?q="
        self.genius_song = "https://api.genius.com/songs/"
        self.genius_access_token = "MzQaNvA53GOGvRTV8OXUbq2NCMahcnVre5EZmj-OcSjVleVO4kNwMVZicPsD5AL7"

        self.sanity_checks = True
        self.sanity_min_title_ratio = 0.6
        self.sanity_min_artist_ratio = 0.7

        self.history = []
        self.failed = []  # All files that failed
        if not self.ignore_history:
            self._load_history()

        self.rm_explicit = rm_explicit

    def __del__(self):
        if self.write_history:
            self._write_history()

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

        with open(config_path + "history", "w") as history_file:
            for file in self.history:
                history_file.write(file + "\n")

        with open(config_path + "failed", "w") as failed_file:
            for file in self.failed:
                failed_file.write(file + "\n")

    def get_urls_azlyrics(self, artist:str, title:str):
        """
        Create a azlyrics html from the artist and title
        If the title contains parenthesis or äüö, there will be multiple versions, one that contains the (...)öäü and one that doesn't.
        """
        # convert to lower case
        artist = artist.casefold()
        title = title.casefold()

        # remove 'a' or 'the' from the artist
        if artist[0:2] == "a ":
            artist = artist[2:]
        elif artist[0:4] == "the ":
            artist = artist[4:]

        # remove anything in square brackets (eg [Explicit])
        for match in re.finditer(r"\[.*\]", title):
            title = title.replace(match.group(), "")

        titles = [title]

        # if title has(), create one version with and one without them
        if re.search(r"\(.*\)", title):
            for match in re.finditer(r"\(.*\)", title):
                title = title.replace(match.group(), "")
            titles.append(title)

        # some special chars
        toNone = [' ', '-', ',', '.', '…', '\'', '"', '°', '`', '´', '/', '!', '?', '#', '*', '(', ')']
        for c in toNone:
            artist = artist.replace(c, "")

        #
        # replace umlaute, create multiple versions
        #
        old = ['ä', 'ö', 'ü', 'ß', '&']
        new1 = ['a', 'o', 'u', 'ss', "and"]
        new2 = ['', '', '', '', "and"]

        # in artist
        if any(c in old for c in artist):
            for i in range(len(old)):
                artist = artist.replace(old[i], new1[i])
        # multiple loops are needed since the array might grow

        # umlaute
        for n in range(len(titles)):
            if any(c in old for c in titles[n]):
                # replace titles[n] with the first version and append the second
                title2 = titles[n]
                for i in range(len(old)):
                    titles[n] = titles[n].replace(old[i], new1[i])
                    title2 = title2.replace(old[i], new2[i])
                titles.append(title2)

        # features
        for title in titles:
            match = re.search(r"fe?a?t\.?.*", title)
            if match:
                titles.append(title.replace(match.group(), ""))

        # spaces, etc
        for n in range(len(titles)):
            for c in toNone:
                titles[n] = titles[n].replace(c, '')

        #
        # create urls
        #
        urls = []
        for title in titles:
            urls.append("https://azlyrics.com/lyrics/" + artist + '/' + title + ".html")
        return urls

    def get_lyrics_azlyrics(self, urls):
        """
        Extract the lyrics from the html
        """

        message = ""
        for url in urls:
            # visit the url
            html = None
            try:
                html = str(urllib.request.urlopen(url).read().decode("utf-8"))
                sleep(self.delay) # azlyrics blocks requests if there is no delay
            except Exception:
                sleep(self.delay) # azlyrics blocks requests if there is no delay
                message += f"Could not access url: {url}\n    "
                continue

            lyrics = None
            match = re.search(r"<!\-\- Usage of azlyrics.com content by any third\-party lyrics provider is prohibited by our licensing agreement. Sorry about that. \-\->(.|\n)+?</div>", html)
            if match:
                lyrics = match.group()
                for key, value in {
                    "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->": "",
                    "</div>": "",
                    "\n": "",
                    "<br>": "\n",
                }.items():
                    lyrics = lyrics.replace(key, value)

                # remove all html tags
                for tag in re.finditer(r"<.+>", lyrics):
                    lyrics = lyrics.replace(tag.group(), "")
                for tag in re.finditer(r"</.+>", lyrics):
                    lyrics = lyrics.replace(tag.group(), "")

                return (True, lyrics)

            message += f"Could not find lyrics in html for {url}\n    "
        message = message.strip(" \n")
        return (False, message)

    def get_url_genius(self, artist:str, title:str):
        """
        Retrieve the url using the genius api:
        1) Get song id using search for song + artist
        2) Get url from song id
        """
        # get search results
        query_search = self.genius_search + urllib.parse.quote(f"{artist} {title}")
        request_search = urllib.request.Request(query_search)
        request_search.add_header("Authorization", f"Bearer {self.genius_access_token}")
        try:
            results = loads(urllib.request.urlopen(request_search).read())["response"]["hits"]
        except urllib.error.URLError:
            return (False, f"Could not access url: {query_search}")

        message = ""
        url = None
        i = 0
        while url is None and i < len(results):
            # check if result is song and then get url
            if results[i]["type"] == "song":
                song_id = results[i]["result"]["id"]
                # check if result is garbage by checking how similar title and artist names are
                if self.sanity_checks:
                    genius_artist = results[i]["result"]["primary_artist"]["name"]
                    genius_artist_featured = results[i]["result"]["artist_names"]
                    genius_title = results[i]["result"]["title"]
                    genius_title_featured = results[i]["result"]["title_with_featured"]
                    if SequenceMatcher(None, title.lower(), genius_title.lower()).ratio() < self.sanity_min_title_ratio:
                        if SequenceMatcher(None, title.lower(), genius_title_featured.lower()).ratio() < self.sanity_min_title_ratio:
                            message += f"Genius result: titles do not match enough: '{title}' and '{genius_title}'/'{genius_title_featured}'\n    "
                            i += 1
                            continue

                    if SequenceMatcher(None, artist.lower(), genius_artist.lower()).ratio() < self.sanity_min_artist_ratio:
                        if SequenceMatcher(None, artist.lower(), genius_artist_featured.lower()).ratio() < self.sanity_min_artist_ratio:
                            message += f"Genius result: artists do not match enough: '{artist}' and '{genius_artist}'/'{genius_artist_featured}'\n    "
                            i += 1
                            continue
                request_song = urllib.request.Request(f"{self.genius_song}{song_id}")
                request_song.add_header("Authorization", f"Bearer {self.genius_access_token}")
                try:
                    url = loads(urllib.request.urlopen(request_song).read())["response"]["song"]["url"]
                except urllib.error.URLError:
                    message += f"Genius result: Could not access url: '{self.genius_song}{song_id}'\n    "
            i += 1
        if not url:
            message += f"Could not find song lyrics on genius"
            return (False, message)
        return (True, url)

    def get_lyrics_genius(self, url):
        request_lyrics = urllib.request.Request(url)
        # request_lyrics.add_header("Authorization", f"Bearer {self.genius_access_token}")
        request_lyrics.add_header("User-Agent", "Mozilla/5.0")
        try:
            html = urllib.request.urlopen(request_lyrics).read()
        except urllib.error.URLError:
            return (False, f"Could not access url: {url}")

        # extract lyrics from html: lyrics are in divs with "data-lyrics-container=true"
        lyrics = ""
        soup = BeautifulSoup(html, "html.parser")
        for br in soup.find_all("br"):
            br.replaceWith("\n")
        divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
        if not divs:
            return (False, f"Could not find lyrics in html: {url}")
        for div in divs:
            lyrics += div.get_text(separator="")
        return (True, lyrics)

    def process_dir(self, directory):
        f"""
        Process all files from <directory> having a {Nicole.allowed_extensions} fileextension.
        If recursive, call process_dir for subdirectories.
        """
        if not path.isabs(directory):
            directory = path.normpath(getcwd() + "/" + directory)
        if not path.isdir(directory):
            print(f"\nInvalid directory: '{directory}'")
            return 1
        if not self.silent:
            print("\nProcessing directory: " + directory)

        entries = listdir(directory)
        entries.sort()

        for entry in entries:
            entry = path.normpath(directory + "/" + entry)

            if path.isfile(entry):
                extension = path.splitext(entry)[1]

                # if sound file with mp3 tags
                if extension in Nicole.allowed_extensions:
                    self.process_file(entry)

            elif path.isdir(entry) and self.recursive:
                self.process_dir(entry)


    def process_file(self, file):
        """
        process a file, append to history and print a message (depending on settings)
        """
        success, message = self._process_file(file)

        # add to history
        if self.write_history:
            if file not in self.history:
                self.history.append(file)
            if not success:
                self.failed.append(file)

        if not self.silent:
            if success:
                print(f"✓ {file}")
            else:
                print(f"✕ {file}")
            print("    " + message)
        # print("History\n", self.history)
        # print("Failed\n", self.failed)


    def _process_file(self, file):
        """
        search for tags, write them to the file (if not dry run) and return wether successful or not and a message
        """
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

        lyrics = "Sample Lyrics"
        success = False
        site = "Sample Site"
        message = ""
        # try genius
        if self.lyrics_site in ["all", "genius"]:
            success, url = self.get_url_genius(artist, title)
            if success:
                success, lyrics = self.get_lyrics_genius(url)
                if not success:
                    message += lyrics + "\n    "  # lyrics is error message
                site = "genius"
            else:
                message += url + "\n    "  # url is error message
        # try azlyrics
        if not success and self.lyrics_site in ["all", "azlyrics"]:
            urls = self.get_urls_azlyrics(artist, title)
            success, lyrics = self.get_lyrics_azlyrics(urls)
            site = "azlyrics"
            if not success:
                message += lyrics
        # if found lyrics
        if success:
            if self.dry_run:
                print(f"\n\n{artist} - {title}:\n{lyrics}\n")
            # write to tags
            else:
                if type(audio) == id3.ID3:
                    audio.add(id3.USLT(encoding=id3.Encoding.UTF8, lang="   ", text=lyrics))
                    audio.save(v2_version=4)
                elif type(audio) == flac.FLAC:
                    audio["LYRICS"] = lyrics
                    audio.save()
                else:
                    return (False, f"Could find lyrics but failed to write the tag (unknown audio type: {type(audio)})")

            message += f"Written lyrics from {site} to {artist} - {title}"
            return (True, message)
        else:
            return (False, message.strip("\n    "))


def main():
    print(f"Nicole version {version}")

    parser = argparse.ArgumentParser(prog="nicole", description="lyrics scraper and embedder", epilog="https://github.com/MatthiasQuinter/nicole")
    parser.add_argument("--directory", "-d",        action="append",     help="process directory [directory]")
    parser.add_argument("--file", "-f",             action="append",     help="process file [file]")
    parser.add_argument("--recursive", "-r",        action="store_true", help="go through directories recursively")
    parser.add_argument("--silent",                 action="store_true", help="silent, no command-line output")
    parser.add_argument("--ignore-history", "-i",   action="store_true", help="ignore history")
    parser.add_argument("--no-history", "-n",       action="store_true", help="do not write to history")
    parser.add_argument("--overwrite", "-o",        action="store_true", help="overwrite if the file already has lyrics")
    parser.add_argument("--dry-run", "-t",          action="store_true", help="test, do not write lyrics to file, but print to console")
    parser.add_argument("--rm-explicit",            action="store_true", help="remove the \"[Explicit]\" lyrics warning from the songs title tag")
    parser.add_argument("--site", "-s",             action="store",      help="use only [site]: azlyrics or genius", default="all")
    args = parser.parse_args()

    if args.file is None and args.directory is None:
        parser.error("Either --directory or --file is required")

    # create nicole instance
    nicole = Nicole(test_run=args.dry_run, silent=args.silent, write_history=not args.no_history, ignore_history=args.ignore_history, overwrite_tag=args.overwrite,
                            recursive=args.recursive, rm_explicit=args.rm_explicit, lyrics_site=args.site)

    if type(args.file) == list:
        for file in args.file:
            try:
                nicole.process_file(file)
            except KeyboardInterrupt:
                pass
    if type(args.directory) == list:
        for directory in args.directory:
            try:
                nicole.process_dir(directory)
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()

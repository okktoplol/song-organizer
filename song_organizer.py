#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# program renames album directories to a custom format
# Lia Luz <lia@cheesecake.cv>

import discogs_client # https://www.discogs.com/ api client
from tinytag import TinyTag # for checking music files tags
import os

class SongOrganizer:
    # directory: artist directory with albums
    # fmt: format for final directory name, parsed as fstring (must escape '{}' with {{}}), fields:
    #   name = album name
    #   catno = catalogue number (or none)
    #   label = label name (first in object)
    #   year = album release year
    #   artist = album artist (first in object)
    #   country = artist country
    #   genres = genres (object), TODO

    def __init__(self, directory: str = "./", fmt: str = "[{year}] {{{catno}}} {name}", verbose: bool = False):
        # set user token env var to use discogs functionality
        self.d = discogs_client.Client('song_organizer/0.1', user_token=os.getenv("DISCOGS_API_KEY"))
        self.verbose = verbose
        self.albums = {}
        self.fmt = fmt
        os.chdir(directory)

    # goes into directory, finds audio file, gets album metadata and puts into self.albums
    # format: {"/path/to/old_album_directory_name": "album name"}
    def descend_into_dir(self):
        for dirs in os.listdir("./"):
            os.chdir(dirs) # descend
            for file in os.listdir("./"):
                full_file = os.path.join(os.getcwd(), file)
                if full_file.lower().endswith(('.flac', '.mp3', '.mp2', '.mp1', '.ogg', '.wav', '.mp4', '.aiff', '.wma')): # supported formats
                    try:
                        tags = TinyTag.get(full_file)
                        self.albums.update({os.getcwd(): tags.album})
                        break
                    except Exception as e:
                        if self.verbose == True:
                            print(f"exception: {e}, continuing")
            os.chdir("../") # back

    # gets information about every album in self.albums
    # changes self.albums to have the old album path (to-be-renamed) and new album path
    # {"/path/to/old_album_directory_name": "/path/to/new_formatted_album_directory_name"}
    def create_names(self):
        for (old_path, album) in self.albums.items():
            try:
                results = self.d.search(album, type='release')
            except Exception as e:
                if self.verbose == True:
                    print(f"{e}: failed to fetch album {album} on discogs")

            name = album
            try:
                catno = results[0].labels[0].data['catno']
            except:
                catno = "none"
            label = results[0].labels[0].data['name']
            year = results[0].year
            artist = results[0].artists[0]
            country = results[0].country
            genres = results[0].genres

            # source for fstring eval - https://stackoverflow.com/a/53671539
            self.albums.update({old_path: os.path.join(os.getcwd(), eval(f'f"""{self.fmt}"""'))})

    # shows diff
    # asks to [(a)pply]/(k)eep old/(e)dit
    # does operation
    def rename_album(self):
        

# TODO:
#   - cli
#   - thingy that will rename the albums
#   - readme and the other stuff
            
if __name__ == "__main__":
    s = SongOrganizer("/home/lia/media/music/Unlucky Morpheus")

    s.descend_into_dir()

    s.create_names()

    print(s.albums)

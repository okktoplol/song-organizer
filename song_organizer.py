#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# program renames album directories to a custom format
# Lia Luz <lia@cheesecake.cv>

import discogs_client # https://www.discogs.com/ api client
from tinytag import TinyTag # for checking music files tags
import os
import argparse

class SongOrganizer:
    # directory: artist directory with albums, positional argument 1 or set with --directory
    # fmt: format for final directory name, parsed as fstring (must escape '{}' with {{}}),
    # set with --format, fields:
    #   name = album name
    #   catno = catalogue number (or none)
    #   label = label name (first in object)
    #   year = album release year
    #   artist = album artist (first in object)
    #   country = artist country
    #   genres = genres (object), TODO
    # verbose: generic --verbose option for showing all non fatal exceptions and such
    # create_script: creates a shell script with batch rename operation instead of interactive shell,
    # so the user can revise before applying more easily, TODO
    def __init__(self, directory, fmt: str = "[{year}] {{{catno}}} {name}", verbose: bool = False, create_script: bool = False):
        # set user token env var to use discogs functionality
        self.d = discogs_client.Client('song_organizer/0.1', user_token=os.getenv("DISCOGS_API_KEY"))
        self.create_script = create_script
        self.albums = {}
        self.fmt = fmt
        self.verbose = verbose
        self.album_artist = []
        self.initial_dir = directory
        os.chdir(directory)

    # goes into directory, finds audio file, gets album metadata and puts into self.albums
    # also gets artist name while at it and puts into self.album_artist
    # format: {"/path/to/old_album_directory_name": ["album name"]}
    def descend_into_dir(self):
        if self.verbose == True:
            print(":: getting directories names")
        for dirs in os.listdir("./"):
            os.chdir(dirs) # descend
            for file in os.listdir("./"):
                full_file = os.path.join(os.getcwd(), file)
                if full_file.lower().endswith(('.flac', '.mp3', '.mp2', '.mp1', '.ogg', '.wav', '.mp4', '.aiff', '.wma')): # supported formats
                    try:
                        tags = TinyTag.get(full_file)
                        self.albums.update({os.getcwd(): tags.album})
                        self.album_artist.append(tags.artist)
                        break
                    except Exception as e:
                        if self.verbose == True:
                            print(f"exception: {e}, continuing")
            os.chdir("../") # back
            
    # gets information about every album in self.albums
    # changes self.albums to have the old album path (to-be-renamed) and new album path
    # {"/path/to/old_album_directory_name": "/path/to/new_formatted_album_directory_name"}
    def create_names(self):
        iteration = 0
        albums_len = len(self.albums)
        artist = max(set(self.album_artist), key=self.album_artist.count)
        if self.create_script != True:
            print(":: fetching discogs for information and creating album names (if it looks stuck ur probably being rate limited, just wait)")
        for (old_path, album) in self.albums.items():
            iteration += 1
            try:
                # adding the artist to the search query improves accuracy a lot
                results = self.d.search(album, artist=artist, type='release')
                # program feels sluggish if not u dont constantly tell the user its doing something
                # thats why this is not behind --verbose
                # but it cant get on the script if that option is enabled
                if self.create_script != True:
                    print(f"{iteration}/{albums_len}")
            except Exception as e:
                if self.verbose == True:
                    print(f"{e}: failed to fetch album {album} on discogs")

            name = album
            try:
                catno = results[0].labels[0].data['catno']
            except:
                catno = "none"
            
            # probably all of these need to be in try except block but im not using it so i just commented the ones im not using out
            # TODO: fix
            
            # label = results[0].labels[0].data['name']
            try:
                year = results[0].year
            except:
                year = "idk"
            # artist = results[0].artists
            # country = results[0].country
            # genres = results[0].genres

            # source for fstring eval - https://stackoverflow.com/a/53671539
            self.albums.update({old_path: os.path.join(os.getcwd(), eval(f'f"""{self.fmt}"""'))})

    # shows diff
    # asks to [Y/n]
    # does operation
    # OR
    # create bash script
    def rename_album(self):
        if self.create_script == False:
            for (old_path, new_path) in self.albums.items():
                while True:
                    prompt = input(f":: rename {os.path.basename(old_path)} to {os.path.basename(new_path)}? [Y/n] ").lower()

                    if prompt == "yes" or prompt == "y" or prompt == "":
                        try:
                            os.replace(old_path, new_path) # if this fails open an issue, directory will just be skipped
                        except Exception as e:
                            print(f"{e}: couldnt rename the directory, open an issue, skipping")
                        break
                    elif prompt == "no" or prompt == "n":
                        print("skipping")
                        break
                    else:
                        print("invalid option, try again")
        elif self.create_script == True:
            print("#!/usr/bin/env bash\n")
            for (old_path, new_path) in self.albums.items():
                print(f'mv "{old_path}" "{new_path}"')
            print('\necho "done"')

# TODO:
#   - a way to handle album folders which have "CD1" and "CD2" inside
#   - a "daemon" mode to automatically sort from soulseek finished downloads directory and into
#     the right artist folders, + automatically create artist folders
            
if __name__ == "__main__":  
    parser = argparse.ArgumentParser("song_organizer")
    parser.add_argument("directory", help="Directory containing the albums which should be renamed", type=str)
    parser.add_argument("-f", "--format", default="[{year}] {{{catno}}} {name}", help="Album format when renamed, python fstring, see documentation for options", type=str) # TODO: add options in documentation
    parser.add_argument("--verbose", action='store_true', default=False, help="Shows errors that were handled and other misc stuff")
    parser.add_argument("--output-script", action='store_true', default=False, help="Instead of an interactive command line app, simply outputs a shell script you can pipe to a file and run to apply renaming changes")

    args = parser.parse_args()
    
    s = SongOrganizer(args.directory, args.format, args.verbose, args.output_script)

    s.descend_into_dir()
    s.create_names()
    s.rename_album()

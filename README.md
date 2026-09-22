# song_organizer
a simple python script for organizing albums and formatting album names using both embedded song metadata and discogs information about albums

## usage
- run ```python3 song_organizer.py path-to-directory```
- use the option ```--output-script``` if you'd like a bash script with the changes to be outputted to stdout instead of being prompted to apply them in a cli, ```python3 song-organizer.py path-to-directory --output-script > script.sh``` creates a file called ```script.sh``` with the alteration then you can revise, ```chmod +x``` it and run it to apply the changes
- use to option ```-f``` and specify a format (following python f-strings) to use when renaming
##### format options
- {name}: album name
- {catno}: catalogue number
- {year}: release year
- {artist}: main album artist
- {country}: country of the main album artist

## installation & setup
- clone repo
- install python3
- install required libraries: ```pip install -r requirements.txt```
- set the ```DISCOGS_API_KEY``` to a valid discogs user token, [howto](https://python3-discogs-client.readthedocs.io/en/latest/authentication.html#user-token-authentication)
- I only tested it on linux, but it probably also works on mac, idk about windows

## roadmap
- [x] basic functionality
- [] functionality for creating a shell script to rename instead of using built in python functions
- [] way to handle folders with "CD1" and "CD2" subfolders
- [] daemon mode to watch folder and automatically sort stuff that goes inside it
- [] small mode to rename song names based on metadata alone
- [] extended documentation

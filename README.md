# File Finder

This is a fairly small script written for **Python 3** that can be used to find all files of a given directory and copies them to another directory
The idea came to me from when I heard of a USB stick you can buy from Amazon that comes with a program that will search your computer for all pictures and save them onto the memory stick

------

## What you need to get started

### config.yml

There are 3 diffenent settings you'll need to configure:

- `extensions_to_find`
  - This is a yaml list of all the extensions you want to find
    - Simply copy the format of what's already there to change the extensions you want to look for
  - Don't forget the `.` in the extension you're looking for
- `path_to_scan`
  - This is the path you want to scan
- `path_to_copy_to`
  - This is the path you want to copy the files to

### Installing modules

There are 2 ways to get yourself setup to run this script, either:

- ~~Run `pip install -r requirements.txt`~~
- ~~Run `pip install .`~~
  - If pip isn't in your path you may need to run something like `python -m pip...`

### Running the script

Simply run `python find_files.py`
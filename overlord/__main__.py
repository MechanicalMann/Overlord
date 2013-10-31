import argparse
import multiprocessing
import time
import library

import os
import random
import mutagen #audio metadata module
import mimetypes


# Add .m4a as a valid MIME type.
mimetypes.add_type('audio/mp4', '.m4a')

parser = argparse.ArgumentParser(description="The Radio Robot Overlord")
parser.add_argument('directories', metavar="DIR", nargs="*", help="One or more directories to watch for changes.")

def main():
    multiprocessing.freeze_support()
    
    # This next logic is temporary
    args = parser.parse_args()

    try:
        library.watch_paths(args.directories)
    except:
        print "Unable to start controlling the airwaves."
        raise

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Goodbye."
    finally:
        exit()

# uses MIME to determine if a file is audio; based on extension.
def isAudio(f):
    return (mimetypes.guess_type(f)[0] and mimetypes.guess_type(f)[0].startswith('audio'))

# prints full pathnames to all valid audio files in 'path'
def getFiles(path):
    for root, dirs, files in os.walk(path, followlinks=True):
        for filename in files:
            if (isAudio(filename)):
                print os.path.join(root, filename)

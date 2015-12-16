import argparse
import multiprocessing
import time
import library

import os
import random
import mutagen # audio metadata module
import wave    # because mutagen doesn't do PCM wave files
import re
import datetime
import hashlib

import overlord
from overlord.library.database import *

parser = argparse.ArgumentParser(description="The Radio Robot Overlord")
parser.add_argument('directories', metavar="DIR", nargs="*", help="One or more directories to watch for changes.")

def main():
    multiprocessing.freeze_support()
    


    # This next logic is temporary
    args = parser.parse_args()

    #try:
    #    library.watch_paths(args.directories)
    #except:
    #    print "Unable to start controlling the airwaves."
    #    raise

    # quick n' dirty proof of concept, operates only on first directory passed in
    
    db_path=os.path.dirname(__file__)
        





    # half-assedly parse the first directory from the commandline into the DB, as music
    # TODO: parse all directories, into their proper categories
    # TODO: thread this initial parse
    with OverlordDB(db_path) as db:
        
        # os.walk uses os.listdir, which will return unicode strings if it is
        #   passed a unicode string argument, and byte strings otherwise
        #
        # the sqlite3 backend stores ALL strings as unicode
        #
        # if you make a set of unicode strings and a set of byte strings and
        #   try to do set operations on them, you're gonna have a bad time.
        #
        # the system that this is being developed on has a utf-8 locale
        # I _assume_ there's some way to get the system locale, 
        #   but until I have time to research it, I'm just making the argument to
        #   os.walk unicode by blindly decoding the string with a utf-8 locale
        # I expect this to break horribly on any system with a different locale
        #
        # tl;dr: UNICODE IS HARD, but we're using unicode strings for file paths

        current = set([a.filename for a in AudioFile.select()])
        ondisk = set(getFiles(args.directories[0].decode('utf-8')))

        # let's do some set differences.
        new_files = ondisk - current
        deleted_files = current - ondisk
        rescan_files = current - deleted_files
        
        if len(new_files) > 0:
            print("Adding new files~!")
            with db.transaction():
                for i in new_files:
                    a = AudioFile()
                    a.filename = i
                    (a.artist, a.title) = getMetadata(i)
                    a.duration = getDuration(i)
                    a.file_hash = getChecksum(i)
                    a.last_played = datetime.datetime.min 
                    a.category = "music"
                    a.save()
        
        if len(rescan_files) > 0:
            print("Rescanning existing files!")
            with db.transaction():
                for i in rescan_files:
                    a = AudioFile.get(AudioFile.filename == i)
                    checksum = getChecksum(i)
                    if a.file_hash != checksum:
                        # update the metadata
                        (a.artist, a.title) = getMetadata(i)
                        # it's unlikely but possible the duration has changed
                        # so update that too
                        a.duration = getDuration(i)
                        # setting this to the pre-computed checksum
                        a.file_hash = checksum
                        a.save()

        if len(deleted_files) > 0:
            print("Removing deleted files.")
            with db.transaction():
                for i in deleted_files:
                    a = AudioFile.get(AudioFile.filename == i)
                    a.delete_instance()
        
    # initialize the time a file must not have been played before to now
    # this will be useful once we also determine a "freshness" time period. for now it's just redundant
    last_played_before = datetime.datetime.now()

    try:
        while 1:

            # update time limit
            last_played_before = datetime.datetime.now()
            print last_played_before
            
            # this is probably an expensive query once the dataset gets large. profile and optimize later.
            #music = AudioFile.select().where((AudioFile.category == "music") & (AudioFile.last_played < last_played_before))
            #
            #for t in music:
            #    print t.filename, "\n\t", t.artist, t.title, t.duration 

            
            # pick a random tune, display it.
            t = AudioFile.select().where((AudioFile.category == "music") and (AudioFile.last_played < last_played_before)).order_by(fn.Random()).limit(1).get()
            print t.filename, "\n\t", t.artist, t.title, t.duration, t.last_played
            
            # update the last played time
            t.last_played = datetime.datetime.now()
            t.save()
            
            # chill for a sec
            time.sleep(1)
            
            # spacing pretty print line
            print "\n"

    except KeyboardInterrupt:
        print "Goodbye."
    finally:
        exit()



####
# utility functions
####


def isAudio(f):
    '''Use regular expressions to determine if a file is an audio file.
    Returns a bool.
    '''
    return (re.match(".*\.(mp[34]|m4a|ogg|wav|flac?|aiff?)$", f, re.I) != None)

# prints full pathnames to all valid audio files in 'path'
def getFiles(path):
    list_of_files = []
    for root, dirs, files in os.walk(path, followlinks=True):
        for filename in files:
            if (isAudio(filename)):
                #print os.path.join(root, filename)
                list_of_files.append(os.path.join(root, filename))
    return list_of_files

def getMetadata(audio_file):
    
    artist = "Unknown Artist"
    title = "Unknown Title"

    if audio_file.lower().endswith('.wav'):
        # leave artist as Unknown
        # the title will be the filename, no extension
        title = os.path.split(audio_file)[1][:-4]
    else:
        audio = mutagen.File(audio_file, easy=True)
        try:
            artist = audio["artist"]
        except KeyError:
            pass # key isn't defined, roll with it
        try:
            title = audio["title"]
        except KeyError:
            pass # key isn't defined, roll with it
    
    return artist, title

def getDuration(audio_file):
    ''' Returns the duration of audio_file, in seconds.
        Retval will be a float, may contain fractional seconds.
    '''

    # wave files involve MATHS, because mutagen doesn't deal with wave files
    if audio_file.lower().endswith('.wav'):
        try:
            wav_file = wave.open(audio_file, 'r')
            # nframes / framerate should give time in seconds, 
            # float conversion is present to ensure fractional seconds exist
            time_sec = float(wav_file.getnframes()) / wav_file.getframerate()
            wav_file.close()
        except:
            raise

    else:
        audio = mutagen.File(audio_file, easy=True)    
        time_sec = audio.info.length

    return time_sec

def getChecksum(audio_file):
    ''' Returns a hash of a file's contents, as a hexadecimal string
        Currently uses md5
    '''
    cksum = hashlib.md5()
    with open(audio_file, "rb") as f:
        for chunk in iter(lambda: f.read(128 * cksum.block_size), b""):
            cksum.update(chunk)
    return cksum.hexdigest()

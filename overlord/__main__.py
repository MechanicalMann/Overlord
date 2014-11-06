import argparse
import multiprocessing
import time
import library

import os
import random
import mutagen #audio metadata module
import wave    #because mutagen doesn't do PCM wave files
import mimetypes
import collections

# Add .m4a as a valid MIME type.
mimetypes.add_type('audio/mp4', '.m4a')

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
    music = getFiles(args.directories[0])
    recently_played = collections.deque(music, len(music)/2)

    try:
        while 1:
            # pick a random tune, display it.
            t = random.choice(music)
            while t in recently_played:
                t = random.choice(music)
                # ok got a track not in the queue
            print t, "\n\t", getMetadata(t), getDuration(t)
            recently_played.append(t)

            time.sleep(0.5)
    except KeyboardInterrupt:
        print "Goodbye."
    finally:
        exit()



####
# utility functions
####


def isAudio(f):
    '''Use mimetype to determine if a file is an audio file.
    Annoyingly, playlists count as 'audio', so strip those.
    '''
    mime = mimetypes.guess_type(f)[0]
    return (mime and mime.startswith('audio') and not mime.endswith(('x-mpegurl','x-scpls')))

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

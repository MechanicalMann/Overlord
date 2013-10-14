import argparse
import multiprocessing
import time
import library

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
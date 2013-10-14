import sys
import inotify
from inotify import watcher
from overlord.library import DirectoryWatcher, UpdateAction

class LinuxWatcher(DirectoryWatcher):
    """
    Filesystem watcher for Linux systems.
    """

    def watch(self):
        w = watcher.AutoWatcher()
        w.add_all(self.path, inotify.IN_CREATE | inotify.IN_MODIFY | inotify.IN_DELETE | inotify.IN_MOVED_FROM | inotify.IN_MOVED_TO)

        while 1:
            lastfile = ""
            lastaction = ""

            for result in w.read():
                for event in inotify.decode_mask(result.mask):
                    if event == "IN_CREATE":
                        self.queue.put(UpdateAction(UpdateAction.ADDED, result.fullpath))
                    elif event == "IN_DELETE":
                        self.queue.put(UpdateAction(UpdateAction.DELETED, result.fullpath))
                    elif event == "IN_MODIFY":
                        self.queue.put(UpdateAction(UpdateAction.UPDATED, result.fullpath))
                    elif event == "IN_MOVED_FROM":
                        if lastaction == "IN_MOVED_TO":
                            self.queue.put(UpdateAction(UpdateAction.MOVED, result.fullpath, lastfile))
                        else:
                            lastfile = result.fullpath
                            lastaction = event
                    elif event == "IN_MOVED_TO":
                        if lastaction == "IN_MOVED_FROM":
                            self.queue.put(UpdateAction(UpdateAction.MOVED, lastfile, result.fullpath))
                        else:
                            lastfile = result.fullpath
                            lastaction = event



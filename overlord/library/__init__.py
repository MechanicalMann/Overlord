"""
Handles watching the filesystem for new files to play,
and aggregating file information into a database.

"""

import sys
import update
from abc import ABCMeta, abstractmethod
from multiprocessing import Process
from multiprocessing.queues import Queue

watchers = []

def watch_paths(paths):
    q = Queue()
    updater = update.Updater(q)
    updater.start()
    for p in paths:
        watcher = get_watcher(p, q)
        watcher.start()
        watchers.append(watcher)

def get_watcher(path, queue):
    if sys.platform == "win32" or sys.platform == "cygwin":
        from overlord.library.windows import WindowsWatcher
        return WindowsWatcher(path, queue)
    if sys.platform == "linux2":
        from overlord.library.linux import LinuxWatcher
        return LinuxWatcher(path, queue)
    # TODO support for OSX?
    else:
        return EmptyWatcher(path, queue)

class DirectoryWatcher(Process):
    """
    Base class for asynchronous filesystem watchers.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def watch(self):
        pass

    def __init__(self, path, queue):
        super(DirectoryWatcher, self).__init__()
        if path is None or path == "":
            raise ValueError("Path to watch cannot be null.")
        if queue is None or not isinstance(queue, Queue):
            raise ValueError("Queue must be an instance of multiprocessing.queues.Queue.")
        self.path = path
        self.queue = queue

    def run(self):
        self.watch()

class EmptyWatcher(DirectoryWatcher):
    def watch(self):
        pass

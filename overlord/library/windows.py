import os
import time
import win32con
import win32file
from overlord.library import DirectoryWatcher, UpdateAction

ACTIONS = {
            1: "Created",
            2: "Deleted",
            3: "Updated",
            4: "Renamed From",
            5: "Renamed To"
}

class WindowsWatcher(DirectoryWatcher):
    """
    Filesystem watcher for Windows systems.
    """
    def watch(self):
        hdir = win32file.CreateFile(self.path, FILE_LIST_DIRECTORY, win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | 
                                    win32con.FILE_SHARE_DELETE, None, win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None)
        lastfile = ""
        lastaction = 0
        lastchange = time.time()
        while 1:
            results = win32file.ReadDirectoryChangesW(hdir, 1024, win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME | 
                                                      win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES | win32con.FILE_NOTIFY_CHANGE_SIZE | 
                                                      win32con.FILE_NOTIFY_CHANGE_LAST_WRITE | win32con.FILE_NOTIFY_CHANGE_SECURITY,
                                                      None, None)
            now = time.time()
            if now - lastchange < 1:
                skipdupes = True
            else:
                skipdupes = False
            lastchange = now

            for action, filename in results:
                fullfilename = os.path.join(self.path, file)
                if action == 1:
                    self.queue.put(UpdateAction(UpdateAction.ADDED, fullfilename))
                elif action == 2:
                    self.queue.put(UpdateAction(UpdateAction.DELETED, fullfilename))
                elif action == 3:
                    if skipdupes and lastaction == action and lastfile == fullfilename:
                        continue
                    lastaction = action
                    lastfile = fullfilename
                    self.queue.put(UpdateAction(UpdateAction.UPDATED, fullfilename))
                elif action == 4:
                    lastfile = fullfilename
                    lastaction = 4
                elif action == 5 and lastaction == 4:
                    self.queue.put(UpdateAction(UpdateAction.MOVED, lastfile, fullfilename))
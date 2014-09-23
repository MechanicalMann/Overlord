from multiprocessing import process

class Updater(process.Process):
    def __init__(self, queue):
        super(Updater, self).__init__()
        self.queue = queue

    def run(self):
        while 1:
            result = self.queue.get()
            # TODO integrate with database library
            text = result.file
            if result.action == UpdateAction.ADDED:
                text += " added."
            elif result.action == UpdateAction.UPDATED:
                text += " updated."
            elif result.action == UpdateAction.MOVED:
                text += " moved to " + result.newfile + "."
            elif result.action == UpdateAction.DELETED:
                text += " deleted."
            else:
                text += " had something happen to it."

            print text

            
class UpdateAction:
    """
    Defines an action that was performed on a file.
    """
    ADDED   = 0
    UPDATED = 1
    MOVED   = 2
    DELETED = 4

    action = ADDED
    filename = ""
    newfile = ""

    def __init__(self, action, filename, newfile = ""):
        self.action = action
        self.filename = filename
        self.newfile = newfile




from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Watcher(FileSystemEventHandler):

    def __init__(self, path, forkloop):
        self.forkloop = forkloop
        self.path = path
        FileSystemEventHandler.__init__(self)

    def start(self):
        """Start file monitoring thread"""
        print "Starting file monitor on", self.path
        observer = Observer()
        observer.schedule(self, path=self.path, recursive=True)
        observer.start()

    # TODO: on_create, moved etc. also
    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return

        print "Change on %s" % event.src_path
        self.forkloop.spawnNewChild()

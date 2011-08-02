

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Watcher(FileSystemEventHandler):

    def __init__(self, paths, forkloop):
        self.forkloop = forkloop
        self.paths = paths
        FileSystemEventHandler.__init__(self)

    def start(self):
        """Start file monitoring thread"""

        for path in self.paths:
            print "Starting file monitor on", path
            observer = Observer()
            observer.schedule(self, path=path, recursive=True)
            observer.start()

    # TODO: on_create, moved etc. also
    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return

        print "Change on %s" % event.src_path

        self.forkloop.spawnNewChild()

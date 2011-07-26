
import time
import os
import signal
import os
import atexit

import requests

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler




class ForkLoop(FileSystemEventHandler):

    def __init__(self):


        # Create child on start
        self.fork = True

        self.parent_pid = os.getpid()
        self.child_pid = None
        self.killed_child = False


    def scheduleFork(self, signum, frame):
        print "Parent got signal", os.getpid()
        self.fork = True

    def signalParent(self):
        """Ask parent to spawn new child"""
        print "Signaling parent with %s" % self.parent_pid
        os.kill(self.parent_pid, signal.SIGUSR1)

    def start(self):
        """Start fork loop"""

        signal.signal(signal.SIGUSR1, self.scheduleFork)
        self.startMonitor()

        print "Fork loop started on process", os.getpid()
        while True:

            if self.fork:
                self.fork = False
                self.child_pid = os.fork()
                if self.child_pid == 0:
                    break
                self.killed_child = False

            time.sleep(1)

        print "New child starting!", os.getpid()

        # Register exit listener. We cannot immediately spawn new child when we
        # get a modified event. Must wait that child has closed database etc.
        atexit.register(self.signalParent)

    def should_stop(self):
        """Stop modified monitor in children"""

        if self.child_pid == 0:
            print "stop monitor", os.getpid()

        return self.child_pid == 0


    def startMonitor(self):
        """Start file monitoring thread"""
        path = os.environ.get("reload_watch_dir", ".")
        observer = Observer()
        observer.schedule(self, path=path, recursive=True)
        print "start observer on", path
        observer.start()


    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return

        if self.killed_child:
            return

        if self.child_pid is None:
            print "No killing yet. Not started child yet"
            return

        if self.child_pid == 0:
            print "Cannot kill from child!"
            return

        print "Change on %s" % event.src_path
        print "Kill child!"
        self.killed_child = True
        os.kill(self.child_pid, signal.SIGTERM)





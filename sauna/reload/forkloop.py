# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä
#
# Authors:
#     Esa-Matti Suuronen <esa-matti@suuronen.org>
#     Asko Soukka <asko.soukka@iki.fi>
#
# This file is part of sauna.reload.
#
# sauna.reload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sauna.reload is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sauna.reload.  If not, see <http://www.gnu.org/licenses/>.

import time
import os
import signal
import atexit

from sauna.reload import autoinclude, fiveconfigure
from sauna.reload.db import FileStorageIndex


class ForkLoop(object):

    def __init__(self):
        # Create child on start
        self.fork = True

        self.active = False
        self.pause = False
        self.killed_child = True


        self.parent_pid = os.getpid()
        self.child_pid = None

        # Timers
        self.boot_started = None
        self.child_started = None

    def startBootTimer(self):
        if not self.boot_started:
            self.boot_started = time.time()

    def startChildBooTimer(self):
        self.child_started = time.time()


    def _waitChildToDieAndScheduleNew(self, signal, frame):
        os.wait()
        self._scheduleFork()

    def start(self):
        """
        Start fork loop.
        """

        self.active = True

        # SIGCHLD tells us that child process has really died and we can spawn
        # new child
        signal.signal(signal.SIGCHLD, self.wait)

        print "Fork loop starting on process", os.getpid()
        while True:

            if self.fork:
                self.fork = False

                if self.pause:
                    continue

                if not self.killed_child:
                    print
                    print "Child died on bootup. Pausing fork loop for now. "
                    print "Fix possible errors and save edits and we'll try booting again."

                    # Child died because of unknown reason. Mark it as killed
                    # and go into pause mode.
                    self.killed_child = True
                    self.pause = True
                    continue

                self.startChildBooTimer()
                self.child_pid = os.fork()
                if self.child_pid == 0:
                    break
                self.killed_child = False

            time.sleep(1)

        self._prepareNewChild()

    def _prepareNewChild(self):
        """
        Prepare newly forked child. Make sure that it can properly read DB
        and install deferred products.
        """

        # Register exit listener. We cannot immediately spawn new child when we
        # get a modified event. Must wait that child has closed database etc.
        atexit.register(self._exitHandler)

        from Globals import DB
        db_index = FileStorageIndex(DB.storage)
        db_index.restore()

        autoinclude.include_deferred()
        fiveconfigure.install_deferred()

        print "Booted up new new child in %s seconds. Pid %s" % (
            time.time() - self.child_started, os.getpid())

    def spawnNewChild(self):
        """
        STEP 1 (parent): New child spawning starts by killing the current
        child.
        """

        # TODO: get rid of prints here. Use exceptions.

        if not self.active:
            print "Loop not started yet"
            return

        # if self.killed_child:
        #     print "Child already killed"
        #     return

        if self.child_pid is None:
            print "No killing yet. Not started child yet"
            return

        if self.child_pid == 0:
            print "Cannot kill from child!"
            return


        self.pause = False

        if not self.killed_child:
            print "sending SIGINT to child"
            os.kill(self.child_pid, signal.SIGINT)
        else:
            # Ok, we already have killed the child, but asking for new child
            print "Not sending SIGINT because we already killed the child. Just scheduling new fork."
            self._scheduleFork()

        self.killed_child = True


    def _exitHandler(self):
        """
        STEP 2 (child): Child is about to die. Fix DB.
        """

        # TODO: Fetch adapter with interface
        # Must import here because we don't have DB on bootup yet
        from Globals import DB
        db_index = FileStorageIndex(DB.storage)
        db_index.save()



    def _scheduleFork(self, signum=None, frame=None):
        """
        STEP 3 (parent): Child told us via SIGUSR1 that we can spawn new child
        """
        self.fork = True

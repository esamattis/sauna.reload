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


from sauna.reload.db import FileStorageIndex



class ForkLoop(object):

    def __init__(self):


        self.active = False

        # Create child on start
        self.fork = True

        self.parent_pid = os.getpid()
        self.child_pid = None
        self.killed_child = False

        self.boot_started = None
        self.boot_started = None
        self.child_started = None


    def startBootTimer(self):
        if not self.boot_started:
            self.boot_started = time.time()

    def startChildBooTimer(self):
        self.child_started = time.time()


    def scheduleFork(self, signum, frame):
        print "Parent got signal", os.getpid()
        self.fork = True


    def start(self):
        """Start fork loop"""

        signal.signal(signal.SIGUSR1, self.scheduleFork)

        self.active = True

        print "Fork loop starting on process", os.getpid()
        while True:

            if self.fork:
                self.fork = False
                self.startChildBooTimer()
                self.child_pid = os.fork()
                if self.child_pid == 0:
                    break
                self.killed_child = False

            time.sleep(1)



        # Register exit listener. We cannot immediately spawn new child when we
        # get a modified event. Must wait that child has closed database etc.
        atexit.register(self.exitHandler)

        from Globals import DB
        db_index = FileStorageIndex(DB.storage)
        db_index.restore()

        self.loadDeferredProducts()

        print "Booted up new new child in %s seconds. Pid %s" % (
            time.time() - self.child_started, os.getpid())


    def loadDeferredProducts(self):
        # import Products.Five.fiveconfigure
        # from sauna.reload import fiveconfiguretools
        # setattr(Products.Five.fiveconfigure, "findProducts",
        #         fiveconfiguretools.findDeferredProducts)

        from Products.Five.zcml import load_config
        import sauna.reload
        load_config("autoinclude.zcml", sauna.reload)

        # setattr(Products.Five.fiveconfigure, "findProducts",
        #         fiveconfiguretools.findProducts)
        # TODO: Find out why developed Five-products were not
        # added into Products._packages_to_initialize.
        # TODO: run install_package for every package added
        # to Products._packages_to_initialize, which are not
        # yet installed.


    def spawnNewChild(self):
        if not self.active:
            print "Loop not started yet"
            return

        if self.killed_child:
            return

        if self.child_pid is None:
            print "No killing yet. Not started child yet"
            return

        if self.child_pid == 0:
            print "Cannot kill from child!"
            return

        print "Kill child!"
        self.killed_child = True
        os.kill(self.child_pid, signal.SIGINT)

    def huuda(self):
        print "AAAAAAA"


    def should_stop(self):
        """Stop modified monitor in children"""

        if self.child_pid == 0:
            print "stop monitor", os.getpid()

        return self.child_pid == 0


    def exitHandler(self):
        """Ask parent to spawn new child"""

        # TODO: Fetch adapter with interface
        # Must import here because we don't have DB on bootup yet
        from Globals import DB
        db_index = FileStorageIndex(DB.storage)
        db_index.save()


        print "Signaling parent pid %s" % self.parent_pid
        os.kill(self.parent_pid, signal.SIGUSR1)






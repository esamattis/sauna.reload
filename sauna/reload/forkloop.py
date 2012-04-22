# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä and Contributors.
#
# All Rights Reserved.
#
# Authors:
#     Esa-Matti Suuronen <esa-matti@suuronen.org>
#     Asko Soukka <asko.soukka@iki.fi>
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS

"""The Fork Loop (tm)"""

import time
import os
import signal
import atexit

from zope.event import notify
from App.config import getConfiguration

from Signals.SignalHandler import SignalHandler
registerHandler = SignalHandler.registerHandler

from sauna.reload import autoinclude, fiveconfigure
from sauna.reload.interfaces import IDatabaseHooks
from sauna.reload.events import NewChildForked, NewChildIsReady
from sauna.reload.utils import errline, logger


class CannotSpawnNewChild(Exception):
    pass


class ForkLoop(object):

    def __init__(self):

        self.fork = True  # Create child on start
        self.active = False
        self.pause = False
        self.killed_child = True
        self.forking = False
        self.exit = False

        self.parent_pid = os.getpid()
        self.child_pid = None

        # Timers
        self.boot_started = None
        self.child_started = None

        self.cfg = None
        self.database = None

    def isChild(self):
        return self.child_pid == 0

    def startBootTimer(self):
        if not self.boot_started:
            self.boot_started = time.time()

    def startChildBooTimer(self):
        self.child_started = time.time()

    def isChildAlive(self):

        if self.isChild():
            return True

        return (self.child_pid is not None
            and os.path.exists("/proc/%i" % self.child_pid))

    def _scheduleFork(self, signum=None, frame=None):
        self.fork = True

    def _childIsGoingToDie(self, signum=None, frame=None):
        self.killed_child = True

    def start(self):
        """
        Start fork loop.
        """

        # Load configuration here to make sure that everything for it is loaded
        self.cfg = getConfiguration()

        # Must import here because we don't have DB on bootup yet
        from Globals import DB
        self.database = IDatabaseHooks(DB)

        # SIGCHLD tells us that child process has really died and we can spawn
        # new child
        registerHandler(signal.SIGCHLD, self._waitChildToDieAndScheduleNew)

        # With SIGUSR1 child can tell that it dies by request, not by exception
        # etc.
        registerHandler(signal.SIGUSR1, self._childIsGoingToDie)

        self.loop()

    def loop(self):
        """
        Magic happens here
        """

        registerHandler(signal.SIGINT, self._parentExitHandler)
        registerHandler(signal.SIGTERM, self._parentExitHandler)

        self.active = True

        logger.info("Fork loop starting on parent. PID %i" % os.getpid())
        while True:
            self.forking = False

            if self.exit:
                return

            if self.fork:
                self.fork = False

                if self.pause:
                    # Pause mode. No forks now.
                    continue

                if not self.killed_child:
                    errline()
                    errline("Child died on bootup. "
                            "Pausing fork loop for now.")
                    errline("Fix possible errors and save edits "
                            "and we'll try booting again.")
                    errline("Waiting...")

                    # Child died because of unknown reason. Mark it as killed
                    # and go into pause mode.
                    self.killed_child = True
                    self.pause = True
                    continue

                if self.isChildAlive():
                    # Child is still alive for some reason. Lets wait few
                    # rounds for it to die.
                    continue

                self.forking = True
                self.startChildBooTimer()
                self.child_pid = os.fork()
                if self.child_pid == 0:
                    break
                self.killed_child = False

            time.sleep(1)

        logger.setChildLogger()
        logger.info("Forked new child. Installing reloadable products...")

        self._prepareNewChild()

        self.forking = False

        logger.logDeferredErrors()
        logger.logDeferred()

        logger.info("Booted up new child in %s seconds. PID %i" % (
            time.time() - self.child_started,  os.getpid()))

        notify(NewChildIsReady(self))

    def _prepareNewChild(self):
        """
        Prepare newly forked child. Make sure that it can properly read DB
        and install deferred products.
        """

        # Register exit listener. We cannot immediately spawn new child when we
        # get a modified event. Must wait that child has closed database etc.
        atexit.register(self._childExitHandler)

        # Make sure that PID files and locks stay here, because dying child
        # will clear them.
        self.makeLockFile()
        self.makePidFile()

        self.database.resumeFromReload()

        notify(NewChildForked(self))

        autoinclude.includeDeferred()
        fiveconfigure.installDeferred()

    def spawnNewChild(self):
        """
        STEP 1 (parent): New child spawning starts by killing the current
        child.
        """

        if not self.active:
            raise CannotSpawnNewChild("Loop not started yet")

        if self.forking:
            raise CannotSpawnNewChild("Serious forking action is already "
                                      "going on. Cannot fork now.")

        if self.child_pid is None:
            raise CannotSpawnNewChild("No killing yet. Not started child yet")

        self.pause = False

        if not self.killed_child or self.isChild():
            self._killChild()
        else:
            # Ok, we already have sent the SIGINT the child, but asking for new
            # child
            logger.info("Not sending SIGINT because we already killed "
                        "the child. Just scheduling new fork.")
            self._scheduleFork()

        self.killed_child = True

    def _killChild(self):
        if self.isChild():
            # Signal parent that this is requested kill, not an error situation
            os.kill(self.parent_pid, signal.SIGUSR1)
            # Kill itself
            os.kill(os.getpid(), signal.SIGINT)
        else:
            os.kill(self.child_pid, signal.SIGINT)

    def _parentExitHandler(self, signum=None, frame=None):
        if self.isChild():
            return

        self.exit = True

        if self.isChildAlive():
            logger.info("Parent dying. Killing child first.")
            self._killChild()

    def _childExitHandler(self):
        """
        STEP 2 (child): Child is about to die. Fix DB.
        """

        self.database.prepareForReload()

    def _waitChildToDieAndScheduleNew(self, signal=None, frame=None):
        """
        STEP 3 (parent): Child told us via SIGCHLD that we can spawn new child
        """
        try:
            # Acknowledge dead child
            os.wait()
        except OSError:
            # OSError: [Errno 10] No child processes
            pass
        # Schedule new
        self._scheduleFork()

    # Modified from Zope2/Startup/__init__.py
    def makePidFile(self):

        if not self.cfg.zserver_read_only_mode:
            # write the pid into the pidfile if possible
            try:
                if os.path.exists(self.cfg.pid_filename):
                    os.unlink(self.cfg.pid_filename)
                f = open(self.cfg.pid_filename, 'w')
                f.write(str(self.parent_pid))
                f.close()
            except IOError:
                pass

    # Modified from Zope2/Startup/__init__.py
    def makeLockFile(self):
        if not self.cfg.zserver_read_only_mode:
            from Zope2.Startup.misc.lock_file import lock_file
            lock_filename = self.cfg.lock_filename
            try:
                if os.path.exists(lock_filename):
                    os.unlink(lock_filename)
                lockfile = open(lock_filename, 'w')
                lock_file(lockfile)
                lockfile.write(str(self.parent_pid))
                lockfile.flush()
            except IOError:
                pass

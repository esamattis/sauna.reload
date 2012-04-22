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
# FOR A PARTICULAR PURPOSE.

"""Watchdog-plugin to trigger reload when the developed files are modified"""

import signal

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from Signals.SignalHandler import SignalHandler
registerHandler = SignalHandler.registerHandler

from sauna.reload.forkloop import CannotSpawnNewChild
from sauna.reload.utils import logger


class Watcher(FileSystemEventHandler):

    allowed_extensions = set(("py", "zcml", "po"))

    def __init__(self, paths, forkloop):
        self.forkloop = forkloop
        self.paths = paths
        FileSystemEventHandler.__init__(self)
        self.observers = []

    def start(self):
        """
        Start file monitoring thread
        """

        registerHandler(signal.SIGINT, self._exitHandler)
        registerHandler(signal.SIGTERM, self._exitHandler)

        for path in self.paths:
            logger.info("Starting file monitor on %s" % path)
            observer = Observer()
            self.observers.append(observer)
            observer.schedule(self, path=path, recursive=True)
            observer.start()

    def _exitHandler(self):
        for obs in self.observers:
            obs.stop()

    def on_any_event(self, event):
        ext = event.src_path.split(".")[-1].lower()
        if ext not in self.allowed_extensions:
            return

        logger.info("Got '%s' event on %s" %
            (event.event_type, event.src_path))

        try:
            self.forkloop.spawnNewChild()
        except CannotSpawnNewChild as e:
            logger.error(str(e.args[0]))

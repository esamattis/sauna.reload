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
        """Start file monitoring thread"""

        registerHandler(signal.SIGINT, self._exitHandler)
        registerHandler(signal.SIGTERM, self._exitHandler)

        for path in self.paths:
            logger.info("Starting file monitor on %s" %  path)
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

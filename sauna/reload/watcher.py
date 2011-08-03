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
        if not True in [event.src_path.endswith(s)
                        for s in [".py", ".zcml", ".po"]]:
            return

        print "Change on %s" % event.src_path

        self.forkloop.spawnNewChild()

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

from ZServer.HTTPServer import zhttp_server
from App.config import getConfiguration

from sauna.reload import autoinclude, forkloop, reload_paths, watcher


def startForkLoop(event):

    if not reload_paths:
        print
        print ("No paths in RELOAD_PATH environment variable."
               "Not starting fork loop.")
        print "Set it to your development egg paths to activete reloading"
        print
        print "Example: RELOAD_PATH=src bin/instance fg"
        print
        return

    # Start fs monitor before the forkloop
    watcher.Watcher(reload_paths.getParentPaths(), forkloop).start()

    # Build and execute a configuration file to include meta, configuration and
    # overrides for dependencies of the deferred development packages.
    autoinclude.include_deferred_deps()

    config = getConfiguration()
    zserver = [server for server in config.servers
        if isinstance(server, zhttp_server)][0]

    print "We saved at least %s seconds from boot up time"\
        % (time.time() - forkloop.boot_started)

    print ("Packages marked for reload are listed in here: "
        "http://127.0.0.1:%i/@@saunareload" % (zserver.port))

    forkloop.start()


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

from sauna.reload import autoinclude, forkloop, reload_paths, watcher, monkeypatcher
from sauna.reload.utils import errline


def startForkLoop(event):

    if not monkeypatcher.PATCHED:
        errline()
        errline("sauna.reload is not installed correctly!")
        errline("Your are missing following line from instance part of your buildout:")
        errline()
        errline("    zope-conf-additional = %import sauna.reload")
        errline()
        errline("Not starting fork loop.")
        errline()
        return

    if not reload_paths:
        errline()
        errline("No paths in RELOAD_PATH environment variable."
                "Not starting fork loop.")
        errline("Set it to your development egg paths to activete reloading")
        errline()
        errline("Example: $ RELOAD_PATH=src bin/instance fg")
        errline()
        return

    # Start fs monitor before the forkloop
    watcher.Watcher(reload_paths.getParentPaths(), forkloop).start()

    # Build and execute a configuration file to include meta, configuration and
    # overrides for dependencies of the deferred development packages.
    autoinclude.include_deferred_deps()

    config = getConfiguration()
    zserver = [server for server in config.servers
        if isinstance(server, zhttp_server)][0]

    errline( "We saved at least %s seconds from boot up time" %
        (time.time() - forkloop.boot_started))

    errline("Packages marked for reload are listed in here: "
            "http://127.0.0.1:%i/@@saunareload" % (zserver.port))

    forkloop.start()


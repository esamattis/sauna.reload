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

import time

from ZServer.HTTPServer import zhttp_server
from App.config import getConfiguration

from sauna.reload import\
    autoinclude, forkloop, reload_paths, watcher, monkeypatcher
from sauna.reload.utils import errline, logger


def startForkLoop(event):

    if not monkeypatcher.PATCHED:
        errline()
        errline("sauna.reload is not installed correctly!")
        errline("Your are missing following line from instance part "
                "of your buildout:")
        errline()
        errline("    zope-conf-additional = %import sauna.reload")
        errline()
        errline("Not starting fork loop.")
        errline()
        return

    if not reload_paths:
        errline()
        errline("sauna.reload: No paths in RELOAD_PATH environment variable. "
                "Not starting fork loop.")
        errline("Set it to your development egg paths to activate reloading")
        errline()
        errline("Example:")
        errline("         $ RELOAD_PATH=src/ bin/instance fg")
        errline()
        return

    # Start fs monitor before the forkloop
    watcher.Watcher(reload_paths.getParentPaths(), forkloop).start()

    # Build and execute a configuration file to include meta, configuration and
    # overrides for dependencies of the deferred development packages.
    autoinclude.includeDependenciesForDeferred()
    autoinclude.checkDeferringErrors()

    config = getConfiguration()
    zserver = [server for server in config.servers
        if isinstance(server, zhttp_server)][0]

    logger.info("We saved at least %s seconds from boot up time" %
        (time.time() - forkloop.boot_started))

    logger.info("Overview available at http://127.0.0.1:%i/@@saunareload" %
        (zserver.port))

    forkloop.start()

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

from sauna.reload import reload_paths
from sauna.reload.forkloop import ForkLoop
from sauna.reload.watcher import Watcher
from sauna.reload.utils import errline

from plone.testing import Layer


class ForkLoopLayer(Layer):

    def setUp(self):
        if not reload_paths:
            errline()
            errline("sauna.reload: No paths in RELOAD_PATH environment variable. "
                    "Not starting fork loop.")
            errline("Set it to your development egg paths to activate reloading")
            errline()
            errline("Example:")
            errline("         $ RELOAD_PATH=`pwd`/src/ bin/test -s my.product")
            errline()
            return

        self.forkloop = ForkLoop()

        # Start fs monitor before the forkloop
        Watcher(reload_paths.getParentPaths(), self.forkloop).start()

        self.forkloop.start()

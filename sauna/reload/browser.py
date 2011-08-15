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

import os

from zope.publisher.browser import BrowserView

from sauna.reload import forkloop, reload_paths
from sauna.reload.forkloop import CannotSpawnNewChild
from sauna.reload.utils import logger


class SaunaReload(BrowserView):

    def __call__(self):

        self.reload_paths = reload_paths
        self.forkloop = forkloop
        if self.request.get("fork", False):
            try:
                self.forkloop.spawnNewChild()
            except CannotSpawnNewChild as e:
                logger.error(str(e.args[0]))

        return self.index()

    def getChildPid(self):
        return os.getpid()

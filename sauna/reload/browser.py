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

"""Overview"""

import os

from zope.publisher.browser import BrowserView

from sauna.reload import autoinclude, forkloop, reload_paths
from sauna.reload.forkloop import CannotSpawnNewChild
from sauna.reload.utils import logger


class SaunaReload(BrowserView):

    def __call__(self):
        self.forkloop = forkloop
        if self.request.get('fork', False):
            try:
                self.forkloop.spawnNewChild()
            except CannotSpawnNewChild as e:
                logger.error(str(e.args[0]))
        return self.index()

    def getConfigurationContext(self):
        try:
            from Zope2.App.zcml import _context as configuration_context
            configuration_context  # pyflakes
        except ImportError:
            from Products.Five.zcml import _context as configuration_context
        return configuration_context

    def getSaunaReloadPath(self):
        import sauna.reload
        return os.path.dirname(sauna.reload.__file__)

    def getDeferredZCMLs(self):
        cfgContext = self.getConfigurationContext()
        sauna_reload = self.getSaunaReloadPath()

        values = []
        cwd = os.getcwd() + os.path.sep
        for zcml in getattr(cfgContext, '_seen_files', ()):
            if zcml in reload_paths\
                and zcml not in autoinclude.FAILED_TO_DEFER:
                if not zcml.startswith(sauna_reload):
                    values.append(zcml.replace(cwd, ''))
        return values

    def getChildPid(self):
        return os.getpid()

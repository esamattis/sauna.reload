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

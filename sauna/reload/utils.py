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

import sys
import logging


class LoggerWrapper(object):

    def __init__(self, name):
        self.name = name
        self._deferredErrors = []
        self.setParentLogger()

    def deferedError(self, msg):
        self._deferredErrors.append(msg)

    def logDeferredErrors(self):
        for msg in self._deferredErrors:
            self.error(msg)
        self._deferredErrors = []

    def setParentLogger(self):
        suffix = ".parent"
        self.logger = logging.getLogger(self.name + suffix)

    def setChildLogger(self):
        suffix = ".child"
        self.logger = logging.getLogger(self.name + suffix)

    def __getattr__(self, name):
        return getattr(self.logger, name)


logger = LoggerWrapper("sauna.reload")


def errline(msg="", *rest):
    rest = " ".join(map(str, rest))
    sys.stderr.write(str(msg) + " " + rest + "\n")

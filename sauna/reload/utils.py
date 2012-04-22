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
# FOR A PARTICULAR PURPOSE.

"""Logging utilities"""

import sys
import logging


class LoggerWrapper(object):

    def __init__(self, name):
        self.name = name
        self._deferred = []
        self._deferredErrors = []
        self.setParentLogger()

    def deferred(self, msg):
        self._deferred.append(msg)

    def logDeferred(self):
        for msg in self._deferred:
            self.info(msg)
        self._deferred = []

    def deferredError(self, msg):
        self._deferredErrors.append(msg)

    def logDeferredErrors(self):
        for msg in self._deferredErrors:
            self.error(msg)
        self._deferredErrors = []

    def setParentLogger(self):
        suffix = '.parent'
        self.logger = logging.getLogger(self.name + suffix)

    def setChildLogger(self):
        suffix = '.child'
        self.logger = logging.getLogger(self.name + suffix)

    def __getattr__(self, name):
        return getattr(self.logger, name)


logger = LoggerWrapper('sauna.reload')


def errline(msg="", *rest):
    rest = ' '.join(map(str, rest))
    sys.stderr.write(str(msg) + ' ' + rest + '\n')

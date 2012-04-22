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

"""Module implementation loader with Zope monkey patching abilities"""

import imp
import os
from pkgutil import ImpLoader

from sauna.reload import autoinclude, fiveconfigure

PATCHED = False


class MonkeyPatchingLoader(ImpLoader):
    """
    Lucky for us ZConfig will use PEP 302 module hooks to load this file,
    and this class implements a get_data hook to intercept the component.xml
    loading and give us a point to generate it.

    Thanks to Martijn Pieters for teaching us this trick.
    """

    def __init__(self, module):
        name = module.__name__
        path = os.path.dirname(module.__file__)
        description = ("", "", imp.PKG_DIRECTORY)
        ImpLoader.__init__(self, name, None, path, description)

    def get_data(self, pathname):
        global PATCHED
        PATCHED = True
        if os.path.split(pathname) == (self.filename, 'component.xml'):
            from sauna.reload import reload_paths
            if reload_paths:
                # 1) Defer autoinclude of packages found under reload paths.
                autoinclude.deferConfigurations()
                # 2) Prevent Five from finding packages under reload paths.
                fiveconfigure.deferInstalls()
            # 3) Return dummy config to keep Zope happy.
            return '<component></component>'
        return super(MonkeyPatchingLoader, self).get_data(self, pathname)

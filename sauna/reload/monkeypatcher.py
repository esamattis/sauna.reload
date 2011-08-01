# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä
#
# Authors:
#     Asko Soukka <asko.soukka@iki.fi>
#     Esa-Matti Suuronen <esa-matti@suuronen.org>
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

"""Module implementation loader with Zope monkey patching abilities"""

import imp
import os
from pkgutil import ImpLoader

from sauna.reload import fiveconfiguretools, autoincludetools

class MonkeyPatchingLoader(ImpLoader):
    """Lucky for us ZConfig will use PEP 302 module hooks to load this file,
    and this class implements a get_data hook to intercept the component.xml
    loading and give us a point to generate it.

    Thanks to Martijn Pieters for teaching us this trick."""

    def __init__(self, module):
        name = module.__name__
        path = os.path.dirname(module.__file__)
        description = ("", "", imp.PKG_DIRECTORY)
        ImpLoader.__init__(self, name, None, path, description)

    def get_data(self, pathname):
        if os.path.split(pathname) == (self.filename, "component.xml"):
            # apply our patch and return dummy config to keep zope happy
            autoincludetools.defer_src_eggs()
            # prevent Five from loading packages under development
            # leaving them for ``sauna.reload`` to configure
            import Products.Five.fiveconfigure
            setattr(Products.Five.fiveconfigure, "findProducts",
                    fiveconfiguretools.findProducts)
            return u"<component></component>"
        return super(MonkeyPatchingLoader, self).get_data(self, pathname)

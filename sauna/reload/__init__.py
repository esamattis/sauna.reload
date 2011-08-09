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

"""sauna.reload"""

# Enable sauna.reload's Zope patches and deferrend z3c.autoinclude includes by
# adding ``zope-conf-additional = %import sauna.reload`` into your buildout's
# *plone.recipe.zope2instance*-part.
#
# [instance]
# recipe = plone.recipe.zope2instance
# zope-conf-additional = %import sauna.reload

import sys
import os


from sauna.reload.forkloop import ForkLoop
from sauna.reload.reloadpaths import ReloadPaths

reload_paths = ReloadPaths([os.path.join(os.getcwd(), p)
    for p in os.environ.get("RELOAD_PATH", "").split(":") if p])

forkloop = ForkLoop()
forkloop.startBootTimer()

# Hook into PEP 302 laoder
from sauna.reload.monkeypatcher import MonkeyPatchingLoader
__loader__ = MonkeyPatchingLoader(sys.modules[__name__])


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

"""
sauna.reload
============

Enable sauna.reload's Zope patches and deferrend z3c.autoinclude includes
by adding ``zope-conf-additional = %import sauna.reload``
into your buildout's part with *plone.recipe.zope2instance*-recipe::

  [instance]
  recipe = plone.recipe.zope2instance
  zope-conf-additional = %import sauna.reload
"""

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

# -*- coding: utf-8 -*-
"""sauna.reload"""

# Enable sauna.reload's Zope patches and deferrend z3c.autoinclude includes by
# adding ``zope-conf-additional = %import sauna.reload`` into your buildout's
# *plone.recipe.zope2instance*-part.
#
# [instance]
# recipe = plone.recipe.zope2instance
# zope-conf-additional = %import sauna.reload

import sys

from sauna.reload.reload import forkloop

from sauna.reload.monkeypatcher import MonkeyPatchingLoader

# Hook into PEP 302 laoder
__loader__ = MonkeyPatchingLoader(sys.modules[__name__])

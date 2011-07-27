# Enable sauna.reload's Zope patches by:
# [instance]
# recipe = plone.recipe.zope2instance
# zope-conf-additional = %import sauna.reload

import sys

from sauna.reload.patchloader import PatchLoader

# Hook into PEP 302 laoder
__loader__ = PatchLoader(sys.modules[__name__])

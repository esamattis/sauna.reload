# -*- coding: utf-8 -*-
"""Utilities for deferring installation of development eggs"""

import os.path

from pkg_resources import iter_entry_points

from Products.Five.zcml import load_config
from Products.Five.browser import BrowserView


def defer_src_eggs():
    for ep in iter_entry_points("z3c.autoinclude.plugin"):
        if "src" in ep.dist.location.split(os.path.sep)\
            and ep.dist.project_name != "sauna.reload":
            ep.module_name = "sauna.reload"


class IncludeDeferredView(BrowserView):
    def __call__(self):
        import sauna.reload
        load_config("autoinclude.zcml", sauna.reload)


# In theory, we could also defer installing Five-products
# by monkey patching Products.Five.fiveconfigure.findProducts:
#
# def findProducts():
#     import Products
#     from types import ModuleType
#     products = []
#     for name in dir(Products):
#         product = getattr(Products, name)
#         if isinstance(product, ModuleType) and hasattr(product, "__file__"):
#             if "src" not in getattr(product, "__file__").split(os.path.sep):
#                 products.append(product)
#     return products
#
# import Products.Five.fiveconfigure
# setattr(Products.Five.fiveconfigure, "findProducts", findProducts)
#
# And then find and install (call initialize) deferred Five-products manually.

# -*- coding: utf-8 -*-
"""Utilities for deferring installation of development eggs"""

import os.path


def findProducts():
    import Products
    from types import ModuleType
    products = []
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, "__file__"):
            if "src" not in getattr(product, "__file__").split(os.path.sep):
                products.append(product)
    return products


def findDeferredProducts():
    import Products
    from types import ModuleType
    products = []
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, "__file__"):
            if "src" in getattr(product, "__file__").split(os.path.sep):
                products.append(product)
    return products

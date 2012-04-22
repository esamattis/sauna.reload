# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä and Contributors.
#
# All Rights Reserved.
#
# Authors:
#     Asko Soukka <asko.soukka@iki.fi>
#     Esa-Matti Suuronen <esa-matti@suuronen.org>
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS

"""Utilities for deferring product installations under selected paths"""

from Zope2.App.zcml import load_config


def findProducts():
    """
    Do not find products under sauna.reload's reload paths.
    """
    import Products
    from types import ModuleType
    from sauna.reload import reload_paths
    products = []
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, '__file__'):
            # Do not find products under sauna.reload's reload paths
            if not getattr(product, '__file__') in reload_paths:
                products.append(product)
    return products


def findDeferredProducts():
    """
    Find only those products, which are under some reload path.
    """
    import Products
    from types import ModuleType
    from sauna.reload import reload_paths
    products = []
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, '__file__'):
            # Find only products under sauna.reload's reload paths
            if getattr(product, '__file__') in reload_paths:
                products.append(product)
    return products


def deferInstalls():
    """
    Patch fiveconfigure with findProducts-method,
    which is unable to see the reloaded paths.
    """
    try:
        import OFS.metaconfigure
        setattr(OFS.metaconfigure, 'findProducts', findProducts)
    except ImportError:
        import Products.Five.fiveconfigure
        setattr(Products.Five.fiveconfigure, 'findProducts', findProducts)


def installDeferred():
    """
    Temporarily patch fiveconfigure with a findProducts-method,
    which is able to see only the products under the reload paths
    and execute Five configuration directives for those.
    """
    import sauna.reload
    try:
        # Zope 2.13
        import OFS.metaconfigure
        setattr(OFS.metaconfigure, 'findProducts', findDeferredProducts)
        load_config('fiveconfigure.zcml', sauna.reload)
        setattr(OFS.metaconfigure, 'findProducts', findProducts)
    except ImportError:
        # Zope 2.12
        import Products.Five.fiveconfigure
        setattr(Products.Five.fiveconfigure, 'findProducts',
                findDeferredProducts)
        load_config('fiveconfigure.zcml', sauna.reload)
        setattr(Products.Five.fiveconfigure, 'findProducts', findProducts)

    # Five pushes old-style product initializations into
    # Products._packages_to_initialize-list.
    # We must loop through that list to find the reloaded packages
    # and try to install them when found.
    from App.config import getConfiguration
    from OFS.Application import install_package
    from Zope2.App.startup import app
    app = app()
    debug_mode = getConfiguration().debug_mode
    from sauna.reload import reload_paths
    try:
        # Zope 2.13
        import OFS.metaconfigure
        # We iterate a copy of packages_to_initialize,
        # because install_package mutates the original.
        packages_to_initialize = [info for info in getattr(
            OFS.metaconfigure, '_packages_to_initialize', [])]
        for module, init_func in packages_to_initialize:
            if getattr(module, '__file__') in reload_paths:
                install_package(app, module, init_func, raise_exc=debug_mode)
    except ImportError:
        # Zope 2.12
        import Products
        # We iterate a copy of packages_to_initialize,
        # because install_package mutates the original.
        packages_to_initialize = [info for info in getattr(
            Products, '_packages_to_initialize', [])]
        for module, init_func in packages_to_initialize:
            if getattr(module, '__file__') in reload_paths:
                install_package(app, module, init_func, raise_exc=debug_mode)
        if hasattr(Products, '_packages_to_initialize'):
            del Products._packages_to_initialize

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

"""Utilities for deferring loading of developed eggs"""

from Zope2.App.zcml import load_config


def findProducts():
    """Do not find products under sauna.reload's reload paths"""
    import Products
    from types import ModuleType
    from sauna.reload import reload_paths
    products = []
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, "__file__"):
            # Do not find products under sauna.reload's reload paths
            if not getattr(product, "__file__") in reload_paths:
                products.append(product)
    return products


def findDeferredProducts():
    """Find only those products, which are under some reload path"""
    import Products
    from types import ModuleType
    from sauna.reload import reload_paths
    products = []
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, "__file__"):
            # Find only products under sauna.reload's reload paths
            if getattr(product, "__file__") in reload_paths:
                products.append(product)
    return products


def defer_install():
    # Patch fiveconfigure with findProducts unable to see reloaded paths
    try:
        import OFS.metaconfigure
        setattr(OFS.metaconfigure, "findProducts", findProducts)
    except ImportError:
        import Products.Five.fiveconfigure
        setattr(Products.Five.fiveconfigure, "findProducts", findProducts)


def install_deferred():
    # Temporarily patch fiveconfigure with findProducts able to see only
    # products under reload paths and execute Five configuration directives
    import sauna.reload
    try:
        import OFS.metaconfigure
        setattr(OFS.metaconfigure, "findProducts", findDeferredProducts)
        load_config("fiveconfigure.zcml", sauna.reload)
        setattr(OFS.metaconfigure, "findProducts", findProducts)
    except ImportError:
        import Products.Five.fiveconfigure
        setattr(Products.Five.fiveconfigure, "findProducts",
                findDeferredProducts)
        load_config("fiveconfigure.zcml", sauna.reload)
        setattr(Products.Five.fiveconfigure, "findProducts", findProducts)

    # Five pushes old-style product initializations into
    # Products._packages_to_initialize-list. We must loop through that list
    # for our reloaded packages and try to install them.
    import Products
    from App.config import getConfiguration
    from OFS.Application import install_package
    from Zope2.App.startup import app
    # FIXME: Is this really the only way to get our app-object?
    app = app()  # XXX: Help! Should we use use app._p_jar-stuff around here?
    debug_mode = getConfiguration().debug_mode
    from sauna.reload import reload_paths
    for module, init_func in getattr(Products, "_packages_to_initialize", []):
        if getattr(module, "__file__") in reload_paths:
            install_package(app, module, init_func, raise_exc=debug_mode)
    if hasattr(Products, "_packages_to_initialize"):
        del Products._packages_to_initialize

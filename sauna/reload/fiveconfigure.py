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


from pkg_resources import iter_entry_points

from sauna.reload import autoinclude


def findProducts():
    import Products
    from types import ModuleType
    from sauna.reload import reload_paths
    products = []
    deferred = [ep.dist.project_name
                for ep in iter_entry_points("z3c.autoinclude.plugin")
                if ep.module_name == autoinclude.DEFERRED_TARGET]
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, "__file__"):
            # Find only those products, which are under some reload path.
            # XXX: Because ``sauna.reload`` doesn't have full Five-support yet,
            # we select (or deselect) only those, which support autoinclude.
            if not getattr(product, "__file__") in reload_paths\
                and product.__name__ not in deferred:
                products.append(product)
    return products


def findDeferredProducts():
    import Products
    from types import ModuleType
    from sauna.reload import reload_paths
    products = []
    deferred = [ep.dist.project_name
                for ep in iter_entry_points("z3c.autoinclude.plugin")
                if ep.module_name == autoinclude.DEFERRED_TARGET]
    for name in dir(Products):
        product = getattr(Products, name)
        if isinstance(product, ModuleType) and hasattr(product, "__file__"):
            # Find only those products, which are under some reload path.
            if getattr(product, "__file__") in reload_paths\
                and product.__name__ in deferred:
                products.append(product)
    return products


def defer_install():
    import Products.Five.fiveconfigure
    setattr(Products.Five.fiveconfigure, "findProducts", findProducts)


def install_deferred():
    pass  # Not yet implemented
    # import Products.Five.fiveconfigure
    # from sauna.reload import fiveconfiguretools
    # setattr(Products.Five.fiveconfigure, "findProducts",
    #         fiveconfiguretools.findDeferredProducts)
    # setattr(Products.Five.fiveconfigure, "findProducts",
    #         fiveconfiguretools.findProducts)
    # TODO: Find out why developed Five-products were not
    # added into Products._packages_to_initialize.
    # TODO: run install_package for every package added
    # to Products._packages_to_initialize, which are not
    # yet installed.

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

"""Utilities for deferring loading of developed eggs"""

import os.path

from pkg_resources import iter_entry_points

from z3c.autoinclude.dependency import DependencyFinder


def defer_src_eggs():
    """Defer autoincluding of products by changing their
    ``z3c.autoinclude.plugin``-entrypoint to target ``sauna.reload`` instead
    of ``plone``"""
    for ep in iter_entry_points("z3c.autoinclude.plugin"):
        # FIXME: We should use the to-be environment variable
        # ``reload_watch_dir`` here, but because this method is invoked, while
        # Zope is only just parsing zope.conf, that environment variable is not
        # yet set and we cannot even use Zope's own tools to parse it from
        # ``zope.conf``.
        if "src" in ep.dist.location.split(os.path.sep)\
            and ep.dist.project_name != "sauna.reload":
            ep.module_name = "sauna.reload"


def get_deferred_deps():
    """Return dictionary with lists of configuration files for the dependencies
    of the deferred eggs"""
    deferred = ["zc.table"]
    # FIXME: Assuming that all dependencies should be autoincluded will
    # probably get us into trouble, but let's see how big trouble. ``zc.table``
    # is an example of a dependency, whose ``configure.zcml`` will not run in
    # Plone environment. Some better solution than just a blacklist would be
    # preferred.
    deps = {"meta.zcml": [], "configure.zcml": [], "overrides.zcml": []}
    for ep in iter_entry_points("z3c.autoinclude.plugin"):
        if ep.module_name == "sauna.reload":
            deferred.append(ep.dist.project_name)
            info = DependencyFinder(ep.dist).includableInfo(
                ["meta.zcml", "configure.zcml", "overrides.zcml"])
            for key in deps:
                deps[key].extend(info.get(key, []))
    for key in deps:
        deps[key] = set([n for n in deps[key] if n not in deferred])
    return deps

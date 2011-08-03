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

"""Utilities for deferring autoinclude of selected paths"""

from pkg_resources import iter_entry_points

from z3c.autoinclude.dependency import DependencyFinder
from Zope2.App.zcml import load_config, load_string

DEFERRED_TARGET = "sauna.reload"


def defer_paths():
    """Defer autoincluding of given paths by changing *z3c.autoinclude.plugin*
    -entrypoints to target DEFERRED_TARGET instead of *plone*"""
    from sauna.reload import reload_paths

    for ep in iter_entry_points("z3c.autoinclude.plugin"):
        if ep.dist.location in reload_paths\
            and ep.dist.project_name != "sauna.reload":
            ep.module_name = DEFERRED_TARGET


def get_deferred_deps_info():
    """Return dictionary with lists of configuration files for the dependencies
    of the deferred eggs"""
    deferred = ["zc.table"]
    # FIXME: Assuming that all dependencies should be autoincluded will
    # probably get us into trouble, but let's see how big trouble. ``zc.table``
    # is an example of a dependency, whose ``configure.zcml`` will not run in
    # Plone environment. Some better solution than just a blacklist would be
    # welcome.
    deps = {"meta.zcml": [], "configure.zcml": [], "overrides.zcml": []}
    for ep in iter_entry_points("z3c.autoinclude.plugin"):
        if ep.module_name == DEFERRED_TARGET:
            deferred.append(ep.dist.project_name)
            info = DependencyFinder(ep.dist).includableInfo(
                ["meta.zcml", "configure.zcml", "overrides.zcml"])
            for key in deps:
                deps[key].extend(info.get(key, []))
    for key in deps:
        deps[key] = set([n for n in deps[key] if n not in deferred])
    return deps


def include_deferred_deps():
    # Build and execute a configuration file to include meta, configuration and
    # overrides for dependencies of the deferred development packages.
    deps = get_deferred_deps_info()
    config = u"""\
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:zcml="http://namespaces.zope.org/zcml">

    """ + u"".join([u"""<include
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="meta.zcml"
        />""" % name for name in deps.get("meta.zcml", ())]) + """

    """ + u"".join([u"""<include
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="configure.zcml"
        />""" % name for name in deps.get("configure.zcml", ())]) + """

    """ + u"".join([u"""<includeOverrides
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="overrides.zcml"
        />""" % name for name in deps.get("overrides.zcml", ())]) + """

</configure>"""
    load_string(config)


def include_deferred():
    """Autoinclude deferred packages"""
    import sauna.reload
    load_config("autoinclude.zcml", sauna.reload)

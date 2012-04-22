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

"""Utilities for deferring autoinclude configurations under selected paths"""

from pkg_resources import iter_entry_points

from z3c.autoinclude.dependency import DependencyFinder
from Zope2.App.zcml import load_config, load_string

import os
from pkg_resources import get_provider
from pkg_resources import working_set as ws
from zope.dottedname.resolve import resolve
from z3c.autoinclude.utils import DistributionManager
from z3c.autoinclude.utils import ZCMLInfo

DEFERRED_TARGET = 'sauna.reload'
FAILED_TO_DEFER = []


def deferConfigurations():
    """
    Defer autoincluding of configurations
    for the packages under the given paths
    by changing *z3c.autoinclude.plugin* -entrypoints
    to target *sauna.reload* instead of *plone*.
    """
    from sauna.reload import reload_paths

    for ep in iter_entry_points('z3c.autoinclude.plugin'):
        if ep.dist.location in reload_paths\
            and ep.dist.project_name != 'sauna.reload':
            ep.module_name = DEFERRED_TARGET


def getDependencyInfosForDeferred():
    """
    Return dictionary with lists of configuration files
    for the dependencies of the deferred eggs.
    """
    deferred = ['zc.table', 'hurry.workflow']
    # XXX: Assuming that all dependencies should be autoincluded
    # will probably get us into trouble, but let's see how big trouble.
    # *zc.table* is an example of a dependency, whose *configure.zcml*
    # will not run in Plone environment.
    # Some better solution than just a blacklist would be welcome.
    from sauna.reload import reload_paths
    zcml_to_look_for = ('meta.zcml', 'configure.zcml', 'overrides.zcml')
    deps = ZCMLInfo(zcml_to_look_for)
    for ep in iter_entry_points('z3c.autoinclude.plugin'):
        if ep.module_name == DEFERRED_TARGET:
            deferred.append(ep.dist.project_name)
            # XXX: We cannot call DependencyFinder(ep.dist).includableInfo,
            # because it eventually imports also our development packages
            # while resolving existence of *zcml_to_look_for*.
            finder = DependencyFinder(ep.dist)
            info = ZCMLInfo(zcml_to_look_for)
            for req in finder.context.requires():
                # Skip missing and deferred requirements
                dist = ws.find(req)  # find req from the current working set
                if dist is None or dist.location in reload_paths:
                    continue
                # Resolve ZCMLs to be loaded for the other requirements
                dist_manager = DistributionManager(get_provider(req))
                for dotted_name in dist_manager.dottedNames():
                    module = resolve(dotted_name)
                    for candidate in zcml_to_look_for:
                        candidate_path = os.path.join(
                            os.path.dirname(module.__file__), candidate)
                        if os.path.isfile(candidate_path):
                            info[candidate].append(dotted_name)
            for key in deps:
                deps[key].extend(info.get(key, []))
    for key in deps:
        deps[key] = set([n for n in deps[key] if n not in deferred])
    return deps


def includeDependenciesForDeferred():
    """
    Build and execute a configuration file
    to include meta, configuration and overrides
    for dependencies of the deferred development packages.
    """
    deps = getDependencyInfosForDeferred()
    config = u"""\
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:zcml="http://namespaces.zope.org/zcml">

    """ + u"".join([u"""<include
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="meta.zcml"
        />""" % name for name in deps.get('meta.zcml', ())]) + """

    """ + u"".join([u"""<include
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="configure.zcml"
        />""" % name for name in deps.get('configure.zcml', ())]) + """

    """ + u"".join([u"""<includeOverrides
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="overrides.zcml"
        />""" % name for name in deps.get('overrides.zcml', ())]) + """

</configure>"""
    load_string(config)


def checkDeferringErrors():
    """
    Check if the configuration files were deferred successfully.
    """
    try:
        from Zope2.App.zcml import _context as configuration_context
        configuration_context  # pyflakes
    except ImportError:
        from Products.Five.zcml import _context as configuration_context

    from sauna.reload import reload_paths
    from sauna.reload.utils import logger

    FAILED_TO_DEFER = []
    cwd = os.getcwd() + os.path.sep
    for zcml in getattr(configuration_context, '_seen_files', ()):
        if zcml in reload_paths:
            logger.deferredError("Cannot reload %s." % zcml.replace(cwd, ''))
            FAILED_TO_DEFER.append(zcml)


def includeDeferred():
    """
    Autoinclude configuration files for the deferred packages
    and log the successfully reloaded configuration files.
    """
    import sauna.reload
    load_config('autoinclude.zcml', sauna.reload)

    # Log the results
    try:
        from Zope2.App.zcml import _context as configuration_context
        configuration_context  # pyflakes
    except ImportError:
        from Products.Five.zcml import _context as configuration_context

    from sauna.reload import reload_paths
    from sauna.reload.utils import logger

    cwd = os.getcwd() + os.path.sep
    for zcml in getattr(configuration_context, '_seen_files', ()):
        if zcml in reload_paths and zcml not in FAILED_TO_DEFER:
            if zcml.startswith(os.path.dirname(sauna.reload.__file__)):
                continue
            logger.deferred("Reloaded %s." % zcml.replace(cwd, ''))

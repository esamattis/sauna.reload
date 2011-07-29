# -*- coding: utf-8 -*-
"""Utilities for deferring installation of development eggs"""

import os.path

from pkg_resources import iter_entry_points

from z3c.autoinclude.dependency import DependencyFinder

from Products.Five.zcml import load_config
from Products.Five.browser import BrowserView


def defer_src_eggs():
    """Defer autoincluding of products by changing their
    z3c.autoinclude.plugin-entrypoint to target "sauna.reload"
    instead of "plone"
    """
    for ep in iter_entry_points("z3c.autoinclude.plugin"):
        if "src" in ep.dist.location.split(os.path.sep)\
            and ep.dist.project_name != "sauna.reload":
            ep.module_name = "sauna.reload"


def get_deferred_deps():
    """Return list of dependencies for deferred eggs"""
    deferred = ["zc.table"]  # FIXME: Assuming that all dependencies
    # should be autoincluded will get us into trouble. "zc.table" is an
    # example of a dependency, whose "configure.zcml" will not run
    # in Plone environment. Some better solution than just a blacklist
    # would be preferred.
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

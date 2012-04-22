# -*- coding: utf-8 -*-
"""Configures p.a.theming-plugins for *sauna.reload*-controlled products"""

from plone.resource.utils import iterDirectoriesOfType

from plone.app.theming.interfaces import THEME_RESOURCE_NAME

from plone.app.theming.plugins.utils import getPlugins
from plone.app.theming.plugins.utils import getPluginSettings

from sauna.reload import reload_paths


def onStartup(event):
    """
    Call onDiscovery() on each plugin for each theme on startup
    """

    plugins = getPlugins()

    for themeDirectory in iterDirectoriesOfType(THEME_RESOURCE_NAME):
        if themeDirectory.directory in reload_paths:  # only for sauna.reload!
            pluginSettings = getPluginSettings(themeDirectory, plugins)

            for name, plugin in plugins:
                plugin.onDiscovery(themeDirectory.__name__,
                                   pluginSettings[name],
                                   pluginSettings)

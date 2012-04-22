# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä and Contributors.
#
# All Rights Reserved.
#
# Authors:
#     Esa-Matti Suuronen <esa-matti@suuronen.org>
#     Asko Soukka <asko.soukka@iki.fi>
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS

"""ZCA Interface Definitions"""

from zope.interface import Interface, Attribute


class IDatabaseHooks(Interface):
    """
    Provides storage-specific hooks to be called during the reload.
    """

    def prepareForReload():
        """
        Is called before the reload (before the process is killed)
        to allow database connection be prepared for it.
        """

    def resumeFromReload():
        """
        Is called after the reload (after a new process has been spawned)
        to allow database connection be restored.
        """


class INewChildForked(Interface):
    """
    Emited immediately after new process is forked. No development packages
    have been yet installed.

    Useful if you want to do something before your code gets loaded.

    Note that you cannot listen this event on a package that is marked for
    reloading as it is not yet installed when this is fired.
    """

    forkloop = Attribute('ForkLoop instance')


class INewChildIsReady(Interface):
    """
    Emitted when all the development packages has been installed to the new
    forked child.

    Useful for notifications etc.
    """

    forkloop = Attribute('ForkLoop instance')

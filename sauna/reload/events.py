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


from zope.interface import Interface, implements


class INewChildForked(Interface):
    """
    Emited immediately after new process is forked. No development packages
    have been yet installed.

    Useful if you want to do something before your code gets loaded.

    Note that you cannot listen this event on a package that is marked for
    reloading as it is not yet installed when this is fired.
    """


class INewChildIsReady(Interface):
    """
    Emitted when all the development packages has been installed to the new
    forked child.

    Useful for notifications etc.
    """


class NewChildForked(object):
    implements(INewChildForked)

    def __init__(self, forkloop):
        self.forkloop = forkloop


class NewChildIsReady(object):
    implements(INewChildIsReady)

    def __init__(self, forkloop):
        self.forkloop = forkloop

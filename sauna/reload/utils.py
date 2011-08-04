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

import os
import sys
import logging
logger = logging.getLogger("sauna.reload")

def errline(msg="", *rest):
    rest =  " ".join(map(str, rest))
    sys.stderr.write(str(msg) + " " + rest + "\n")


class ReloadPaths(object):

    def __init__(self, paths):
        self.paths = [p.rstrip(os.sep) for p in paths]

    def __nonzero__(self):
        return len(self.paths) > 0

    def __contains__(self, test_path):
        test_path = test_path.rstrip(os.sep)

        for path in self.paths:
            if test_path.startswith(path):
                return True
        return False

    def __iter__(self):
        return list(self.paths)

    def findEggPaths(self):

        # TODO: could read directly from configure objects.
        egg_paths = []

        for path in self.paths:
            if os.path.exists(os.path.join(path, "setup.py")):
                egg_paths.append(path)
            else:
                for dirpath, dirnames, filenames in os.walk(path):
                    if "setup.py" in filenames:
                        egg_paths.append(dirpath)

        return sorted(egg_paths)

    def getParentPaths(self):
        parents = []

        parent = None

        for path in sorted(self.paths):

            if parent is None:
                parent = path
                continue

            if path.startswith(parent):
                continue
            else:
                parents.append(parent)
                parent = path

        if parent not in parents:
            parents.append(parent)

        return parents


if __name__ == '__main__':
    paths = [
        "/foo/bar",
        "/newparent",
        "/foo",
        "/foo/child",
        "/another/one",
    ]
    rp = ReloadPaths(paths)
    print list(rp.getParentPaths())

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

from persistent.TimeStamp import TimeStamp

from ZODB.FileStorage.FileStorage import read_index


# TODO: register to ZCA so that ``sauna.reload`` can support also other
# storages than ZODB.
class FileStorageIndex(object):

    def __init__(self, storage):
        self.storage = storage

    def save(self):
        # Save ``Data.fs.index`` before dying to notify the next child of the
        # persistent changes.
        self.storage._lock_acquire()
        try:
            self.storage._save_index()
        finally:
            self.storage._lock_release()

    def restore(self):
        self.storage._lock_acquire()
        try:
            # Load saved ``Data.fs.index`` to see the persistent changes
            # created by the previous child.
            index, start, ltid =\
                self.storage._restore_index() or (None, None, None)
            # Sanity check. Last transaction in restored index must match
            # the last transaction given by FileStorage transaction iterator.
            if ltid and ltid == tuple(self.storage.iterator())[-1].tid:
                self.storage._initIndex(index, {})
                self.storage._pos, self.storage._oid, tid = read_index(
                    self.storage._file, self.storage._file_name, index, {},
                    stop="\377" * 8, ltid=ltid, start=start, read_only=False)
                self.storage._ltid = tid
                self.storage._ts = tid = TimeStamp(tid)
        finally:
            self.storage._lock_release()

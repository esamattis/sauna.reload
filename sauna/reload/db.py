
from persistent.TimeStamp import TimeStamp

from ZODB.FileStorage.FileStorage import read_index

# TODO: register to ZCA so that ``sauna.reload`` is to support also other
# storages than ZODB.
class FileStorageIndex(object):

    def __init__(self, storage):
        self.storage = storage

    def save(self):
        # Save ``Data.fs.index`` before dying to notify the next child of the
        # peristent changes
        self.storage._save_index()
        # TODO: The code aboce should be abstracted with ZCA to make
        # ``sauna.reload`` to be able to support also other storages than ZODB.

    def restore(self):
        # Load saved ``Data.fs.index`` to see the persistent changes created by
        # the previous child.
        index, start, ltid = self.storage._restore_index()
        # Sanity check. Last transaction in restored index must match
        # the last transaction given by FileStorage transaction iterator.
        if ltid == tuple(self.storage.iterator())[-1].tid:
            self.storage._initIndex(index, {})
            self.storage._pos, self.storage._oid, tid = read_index(
                self.storage._file, self.storage._file_name, index, {},
                stop=None, ltid=ltid, start=start, read_only=False)
            self.storage._ltid = tid
            self.storage._ts = tid = TimeStamp(tid)


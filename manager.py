
import fcntl
import os
import time

from srcomp import SRComp

LOCK_FILE = ".update-lock"

def acquire_lock(lock_path):
    fd = open(lock_path, "w")
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd

class SelfDeletingLockableFile(object):
    def __init__(self, path):
        self._path = path

    def __enter__(self):
        self._fd = acquire_lock(self._path)
        return self._fd

    def __exit__(self, exc_type, exc_value, traceback):
        self._fd.close()
        os.remove(self._path)

def update_lock(compstate_path):
    """ Acquire a lock on the given compstate for the purposes of
        updating it. Returns a context manager object which will remove
        the lock and file when __exit__ed. In turn that triggers the
        manager to re load the information it has.
    """
    lock_path = os.path.join(compstate_path, LOCK_FILE)
    return SelfDeletingLockableFile(lock_path)

class SRCompManager(object):
    def __init__(self):
        self.root_dir = "./"
        self.update_time = None

    def _load(self):
        with acquire_lock(self.lock_path):
            "grab a lock & reload"
            #print "Loading compstate from {0}".format(self.root_dir)
            self.comp = SRComp(self.root_dir)
            self.update_time = time.time()

    def _state_changed(self):
        return not os.path.exists(self.lock_path)

    @property
    def lock_path(self):
        return os.path.join(self.root_dir, LOCK_FILE)

    def get_comp(self):
        if self.update_time is None:
            self._load()

        elif time.time() - self.update_time > 5 and self._state_changed():
            "Data is more than 5 seconds old and the state has changed -- reload"
            self._load()

        return self.comp

"""Routines for managing a Compstate instance."""

import contextlib
import errno
import fcntl
import logging
import os
import time

from sr.comp.comp import SRComp


LOCK_FILE = ".update-lock"
UPDATE_FILE = ".update-pls"


def update_lock_path(compstate_path):
    return os.path.join(compstate_path, LOCK_FILE)


def update_pls_path(compstate_path):
    return os.path.join(compstate_path, UPDATE_FILE)


def exclusive_lock(lock_path):
    fd = open(lock_path, "w")
    fcntl.lockf(fd, fcntl.LOCK_EX)
    return fd


def share_lock(lock_path):
    try:
        fd = open(lock_path, "r")
    except IOError as ioe:
        if ioe.errno == errno.ENOENT:
            # Touch the file so it exists
            fd = open(lock_path, "w+")
        else:
            # Some other issue -- fail out
            raise
    fcntl.lockf(fd, fcntl.LOCK_SH)
    return fd


def touch_update_file(compstate_path):
    file_path = update_pls_path(compstate_path)
    open(file_path, 'w').close()


@contextlib.contextmanager
def update_lock(compstate_path):
    """
    Acquire a lock on the given compstate for the purposes of updating it.

    :return: A context manager object which will remove the lock when
             __exit__ed and, if a clean exit, touch the update file. In turn
             that triggers the manager to re load the information it has.
    """

    lock_path = update_lock_path(compstate_path)
    with exclusive_lock(lock_path):
        yield
        touch_update_file(compstate_path)


class SRCompManager(object):
    """An ``SRComp`` manager."""

    def __init__(self):
        self.root_dir = "./"

        self.update_time = None
        """The last time we updated our information."""

        self._update_pls_time = None
        """The time the update pls file was last modified."""

        self._comp = None
        """Cached SRComp instance."""

    def _load(self):
        lock_path = update_lock_path(self.root_dir)
        with share_lock(lock_path):
            # Grab a lock & reload
            logging.info("Loading compstate from %s", self.root_dir)
            self._comp = SRComp(self.root_dir)
            self.update_time = time.time()

    def _state_changed(self):
        update_path = update_pls_path(self.root_dir)
        try:
            new_time = os.path.getmtime(update_path)
        except OSError:
            # It doesn't exist. That's fine -- use a value which won't ever
            # happen so that we load at least the first time through
            new_time = -1

        if new_time != self._update_pls_time:
            self._update_pls_time = new_time
            return True

        return False

    def get_comp(self):
        if self.update_time is None:
            self._load()

        elif time.time() - self.update_time > 5 and self._state_changed():
            # data is more than 5 seconds old and the state has changed, reload
            self._load()

        return self._comp

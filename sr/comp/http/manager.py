
import contextlib
import fcntl
import logging
import os
import time

from sr.comp.comp import SRComp

class SRCompManager(object):
    def __init__(self):
        self.root_dir = "./"
        self.comp = None

    def _load(self):
        logging.info("Loading compstate from {0}".format(self.root_dir))
        self.comp = SRComp(self.root_dir)

    def get_comp(self):
        if self.comp is None:
            self._load()
        return self.comp

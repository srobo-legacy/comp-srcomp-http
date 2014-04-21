
import time

from srcomp import SRComp

class SRCompManager(object):
    def __init__(self):
        self.root_dir = "./"
        self.update_time = None

    def _load(self):
        self.comp = SRComp(self.root_dir)
        self.update_time = time.time()

    def get_comp(self):
        if self.update_time is None:
            self._load()

        elif time.time() - self.update_time > 5:
            "Data is more than 5 seconds old -- reload"
            self._load()

        return self.comp


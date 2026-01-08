
from cache_line import CacheLine
import time

class LRU(CacheLine):
    def __init__(self):
        super().__init__()
        self.time = time.time()

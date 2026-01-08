class CacheLine:
    def __init__(self):
        self.valid = False
        self.tag = None
        self.last_used = 0   # for LRU
        self.insert_time = 0 # for FIFO

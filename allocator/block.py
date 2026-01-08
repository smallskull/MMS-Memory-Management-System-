
class Block:
    def __init__(self, start, size, free=True, block_id=None):
        self.start = start
        self.size = size
        self.free = free
        self.block_id = block_id

    def end(self):
        return self.start + self.size

    def __repr__(self):
        status = "FREE" if self.free else f"USED id={self.block_id}"
        return f"[{self.start}-{self.end()-1}] {status}"

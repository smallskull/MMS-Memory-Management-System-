
from src.allocator.block import Block

class BaseAllocator:
    def __init__(self, total_size):
        self.blocks = [Block(0, total_size)]
        self.next_id = 1
        self.total_size = total_size

    def malloc(self, size):
        raise NotImplementedError

    def free(self, block_id):
        for b in self.blocks:
            if b.block_id == block_id:
                b.free = True
                b.block_id = None
                self.coalesce()
                return True
        return False

    def coalesce(self):
        i = 0
        while i < len(self.blocks)-1:
            if self.blocks[i].free and self.blocks[i+1].free:
                self.blocks[i].size += self.blocks[i+1].size
                self.blocks.pop(i+1)
            else:
                i += 1

    def dump(self):
        return "\n".join(str(b) for b in self.blocks)

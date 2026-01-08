from src.allocator.block import Block

class PhysicalMemory:
    def __init__(self, size):
        self.size = size
        self.blocks = [Block(0, size)]
        self.next_id = 1

    def coalesce(self):
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i].free and self.blocks[i + 1].free:
                self.blocks[i].size += self.blocks[i + 1].size
                self.blocks.pop(i + 1)
            else:
                i += 1

    def dump(self):
        return "\n".join(str(b) for b in self.blocks)

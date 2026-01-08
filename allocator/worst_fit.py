
from src.allocator.base_allocator import BaseAllocator
from src.allocator.block import Block

class WorstFit:
    def malloc(self, memory, size):
        worst_idx = None
        worst_size = -1

        for i, block in enumerate(memory.blocks):
            if block.free and block.size > worst_size:
                worst_size = block.size
                worst_idx = i

        if worst_idx is None or worst_size < size:
            return None

        block = memory.blocks[worst_idx]
        new_block = Block(block.start, size, False, memory.next_id)
        block.start += size
        block.size -= size

        if block.size == 0:
            memory.blocks.pop(worst_idx)

        memory.blocks.insert(worst_idx, new_block)
        memory.next_id += 1
        return new_block.block_id
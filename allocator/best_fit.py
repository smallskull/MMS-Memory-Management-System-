
from src.allocator.base_allocator import BaseAllocator
from src.allocator.block import Block

class BestFit:
    def malloc(self, memory, size):
        best_idx = None
        best_size = float("inf")

        for i, block in enumerate(memory.blocks):
            if block.free and size <= block.size < best_size:
                best_size = block.size
                best_idx = i

        if best_idx is None:
            return None

        block = memory.blocks[best_idx]
        new_block = Block(block.start, size, False, memory.next_id)
        block.start += size
        block.size -= size

        if block.size == 0:
            memory.blocks.pop(best_idx)

        memory.blocks.insert(best_idx, new_block)
        memory.next_id += 1
        return new_block.block_id
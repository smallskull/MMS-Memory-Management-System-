
from src.allocator.base_allocator import BaseAllocator
from src.allocator.block import Block


class FirstFit:
    def malloc(self, memory, size):
        for i, block in enumerate(memory.blocks):
            if block.free and block.size >= size:
                new_block = Block(block.start, size, False, memory.next_id)
                block.start += size
                block.size -= size

                if block.size == 0:
                    memory.blocks.pop(i)

                memory.blocks.insert(i, new_block)
                memory.next_id += 1
                return new_block.block_id
        return None

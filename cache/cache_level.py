import math
from src.cache.cache_line import CacheLine

class CacheLevel:
    def __init__(self, name, cache_size, block_size, associativity, policy):
        self.name = name
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.policy = policy  # "FIFO" or "LRU"

        self.num_blocks = cache_size // block_size
        self.num_sets = self.num_blocks // associativity

        self.offset_bits = int(math.log2(block_size))
        self.set_bits = int(math.log2(self.num_sets))

        self.sets = [
            [CacheLine() for _ in range(associativity)]
            for _ in range(self.num_sets)
        ]

        self.time = 0
        self.hits = 0
        self.misses = 0

    def access(self, address):
        self.time += 1

        block_addr = address // self.block_size
        set_index = block_addr % self.num_sets
        tag = block_addr // self.num_sets

        cache_set = self.sets[set_index]

        # HIT
        for line in cache_set:
            if line.valid and line.tag == tag:
                self.hits += 1
                line.last_used = self.time
                return {
                    "hit": True,
                    "set": set_index,
                    "evicted": False
                }

        # MISS
        self.misses += 1

        victim = None
        for line in cache_set:
            if not line.valid:
                victim = line
                break

        evicted = False
        if victim is None:
            evicted = True
            if self.policy == "LRU":
                victim = min(cache_set, key=lambda l: l.last_used)
            else:
                victim = min(cache_set, key=lambda l: l.insert_time)

        victim.valid = True
        victim.tag = tag
        victim.last_used = self.time
        victim.insert_time = self.time

        return {
            "hit": False,
            "set": set_index,
            "evicted": evicted
        }


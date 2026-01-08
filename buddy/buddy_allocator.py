import math


class BuddyAllocator:
    def __init__(self, size):
        if size & (size - 1) != 0:
            raise ValueError("Buddy allocator size must be a power of two")

        self.size = size
        self.max_order = int(math.log2(size))

        # Free lists: order -> list of block start addresses
        self.free = {i: [] for i in range(self.max_order + 1)}
        self.free[self.max_order].append(0)

        # Allocated blocks: addr -> order
        self.used = {}

    def malloc(self, request_size):
        if request_size <= 0:
            return None

        # Round UP to nearest power of two
        order = math.ceil(math.log2(request_size))

        # Find smallest free block that fits
        for o in range(order, self.max_order + 1):
            if self.free[o]:
                addr = self.free[o].pop()

                # Split until we reach desired order
                while o > order:
                    o -= 1
                    buddy = addr + (1 << o)
                    self.free[o].append(buddy)

                self.used[addr] = order
                return addr

        return None

    def free_block(self, addr):
        if addr not in self.used:
            return False

        order = self.used.pop(addr)

        # Try recursive merging
        while True:
            buddy = addr ^ (1 << order)

            if buddy in self.free[order]:
                self.free[order].remove(buddy)
                addr = min(addr, buddy)
                order += 1
            else:
                break

        self.free[order].append(addr)
        return True

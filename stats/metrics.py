
def fragmentation(blocks):
    free = sum(b.size for b in blocks if b.free)
    largest = max((b.size for b in blocks if b.free), default=0)
    if free == 0: return 0
    return 1 - largest/free

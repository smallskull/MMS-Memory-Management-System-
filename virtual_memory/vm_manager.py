import math
from collections import deque


class PageTableEntry:
    def __init__(self):
        self.valid = False
        self.frame = None


class VirtualMemoryManager:
    def __init__(self, frames, page_size=64, policy="FIFO"):
        self.page_size = page_size
        self.num_frames = frames
        self.policy = policy

        self.page_table = {}      # page_number -> PageTableEntry
        self.frames = [None] * frames  # frame -> page_number

        self.free_frames = deque(range(frames))
        self.replacement_queue = deque()

        self.page_faults = 0

    def access(self, virtual_address):
        page = virtual_address // self.page_size
        offset = virtual_address % self.page_size

        if page not in self.page_table:
            self.page_table[page] = PageTableEntry()

        entry = self.page_table[page]

        # PAGE HIT
        if entry.valid:
            return {
                "page": page,
                "offset": offset,
                "frame": entry.frame,
                "fault": False
            }

        # PAGE FAULT
        self.page_faults += 1

        # Get frame
        if self.free_frames:
            frame = self.free_frames.popleft()
        else:
            # FIFO replacement
            victim_page = self.replacement_queue.popleft()
            victim_entry = self.page_table[victim_page]
            frame = victim_entry.frame

            victim_entry.valid = False
            victim_entry.frame = None

        # Map new page
        entry.valid = True
        entry.frame = frame
        self.frames[frame] = page
        self.replacement_queue.append(page)

        return {
            "page": page,
            "offset": offset,
            "frame": frame,
            "fault": True
        }

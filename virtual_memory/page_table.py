
from src.virtual_memory.page import Page

class PageTable:
    def __init__(self):
        self.table = {}

    def get(self, page):
        if page not in self.table:
            self.table[page] = Page()
        return self.table[page]

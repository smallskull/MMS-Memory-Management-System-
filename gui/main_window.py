import tkinter as tk
from tkinter import ttk

from src.allocator.physical_memory import PhysicalMemory
from src.allocator.first_fit import FirstFit
from src.allocator.best_fit import BestFit
from src.allocator.worst_fit import WorstFit
from src.stats.tracker import StatsTracker
from src.buddy.buddy_allocator import BuddyAllocator
from src.virtual_memory.vm_manager import VirtualMemoryManager
from src.stats.metrics import fragmentation
from src.cache.cache_level import CacheLevel


class MemorySimulatorGUI:
    def __init__(self):
        # ================= BACKEND =================
        self.memory = PhysicalMemory(1024)

        self.algorithms = {
            "First Fit": FirstFit(),
            "Best Fit": BestFit(),
            "Worst Fit": WorstFit(),
        }

        self.algorithm = self.algorithms["First Fit"]

        self.buddy = BuddyAllocator(1024)

        # ---------- CACHE ----------
        self.l1_cache = CacheLevel("L1", 64, 8, 2, "LRU")
        self.l2_cache = CacheLevel("L2", 256, 8, 4, "FIFO")

        self.last_cache_access = {
            "L1": None,
            "L2": None
        }
        # ---------- VIRTUAL MEMORY ----------
        self.vm = VirtualMemoryManager(frames=8, page_size=64, policy="FIFO")
        self.stats = StatsTracker(total_memory=1024)

        # ================= GUI =================
        self.root = tk.Tk()
        self.root.title("Memory Management Simulator")
        self.root.geometry("900x600")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self._build_physical_memory_tab()
        self._build_buddy_tab()
        self._build_cache_tab()
        self._build_vm_tab()
        self._build_stats_tab()



        # ==========================================================
        # VM + CACHE INTEGRATION (CORE LOGIC)
        # ==========================================================

    def _integrated_access(self, virtual_address):
        vm_result = self.vm.access(virtual_address)

        page = vm_result["page"]
        offset = vm_result["offset"]
        frame = vm_result["frame"]
        fault = vm_result["fault"]

        physical_address = frame * self.vm.page_size + offset

        if self.l1_cache.access(physical_address):
            cache_result = "L1 HIT"
        elif self.l2_cache.access(physical_address):
            cache_result = "L2 HIT"
        else:
            cache_result = "MISS → Main Memory"

        return {
            "va": virtual_address,
            "page": page,
            "offset": offset,
            "frame": frame,
            "pa": physical_address,
            "page_fault": fault,
            "cache_result": cache_result
        }
    # ==========================================================
    # PHYSICAL MEMORY TAB
    # ==========================================================
    def _build_physical_memory_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Physical Memory")

        # -------- Controls --------
        top = ttk.Frame(tab)
        top.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top, text="Allocation Strategy:").pack(side=tk.LEFT)

        self.alloc_var = tk.StringVar(value="First Fit")
        ttk.OptionMenu(
            top,
            self.alloc_var,
            "First Fit",
            *self.algorithms.keys(),
            command=lambda x: setattr(self, "algorithm", self.algorithms[x])
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(top, text="Malloc size:").pack(side=tk.LEFT, padx=5)
        self.malloc_entry = ttk.Entry(top, width=10)
        self.malloc_entry.pack(side=tk.LEFT)

        ttk.Button(top, text="Malloc", command=self._malloc).pack(side=tk.LEFT, padx=5)

        ttk.Label(top, text="Free block id:").pack(side=tk.LEFT, padx=5)
        self.free_entry = ttk.Entry(top, width=10)
        self.free_entry.pack(side=tk.LEFT)

        ttk.Button(top, text="Free", command=self._free).pack(side=tk.LEFT, padx=5)

        # -------- Memory Bar --------
        self.mem_canvas = tk.Canvas(tab, height=80, bg="white")
        self.mem_canvas.pack(fill=tk.X, padx=10, pady=10)

        # -------- Text Dump --------
        self.mem_output = tk.Text(tab, height=12)
        self.mem_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._refresh_memory_view()

    def _malloc(self):
        val = self.malloc_entry.get().strip()
        if not val.isdigit():
            return

        size = int(val)
        self.stats.record_request()

        block_id = self.algorithm.malloc(self.memory, size)

        if block_id is not None:
            self.stats.record_success()
            self.memory.coalesce()
        else:
            self.stats.record_failure()

        self._refresh_memory_view()

    def _free(self):
        if self.free_entry.get().isdigit():
            bid = int(self.free_entry.get())
            for b in self.memory.blocks:
                if b.block_id == bid:
                    b.free = True
                    b.block_id = None
                    self.memory.coalesce()
                    break
            self._refresh_memory_view()

    def _refresh_memory_view(self):
        # -------- Text output --------
        self.mem_output.delete("1.0", tk.END)
        self.mem_output.insert(tk.END, self.memory.dump() + "\n")

        frag = fragmentation(self.memory.blocks)
        self.mem_output.insert(
            tk.END, f"\nExternal Fragmentation: {frag:.2%}\n"
        )

        # -------- Visual bar --------
        self._draw_memory_bar()
        self._refresh_stats_view()

    def _physical_used_memory(self):
        return sum(b.size for b in self.memory.blocks if not b.free)

    def _draw_memory_bar(self):
        self.mem_canvas.delete("all")

        total_mem = self.memory.size
        canvas_width = self.mem_canvas.winfo_width()

        # Handle initial draw before window is ready
        if canvas_width <= 1:
            self.root.after(100, self._draw_memory_bar)
            return

        x = 0
        for block in self.memory.blocks:
            block_width = (block.size / total_mem) * canvas_width

            color = "#6ab04c" if block.free else "#eb4d4b"  # green / red
            self.mem_canvas.create_rectangle(
                x, 10, x + block_width, 70, fill=color, outline="black"
            )

            label = f"{block.size}"
            if not block.free:
                label += f" (id {block.block_id})"

            self.mem_canvas.create_text(
                x + block_width / 2, 40, text=label, font=("Arial", 9)
            )

            x += block_width

    # ==========================================================
    # BUDDY TAB
    # ==========================================================
    def _build_buddy_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Buddy Allocator")

        # -------- Controls --------
        top = ttk.Frame(tab)
        top.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top, text="Allocate size:").pack(side=tk.LEFT)
        self.buddy_alloc_entry = ttk.Entry(top, width=10)
        self.buddy_alloc_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(top, text="Allocate", command=self._buddy_malloc).pack(side=tk.LEFT)

        ttk.Label(top, text="Free address:").pack(side=tk.LEFT, padx=10)
        self.buddy_free_entry = ttk.Entry(top, width=10)
        self.buddy_free_entry.pack(side=tk.LEFT)

        ttk.Button(top, text="Free", command=self._buddy_free).pack(side=tk.LEFT)

        # -------- Buddy Memory Bar --------
        self.buddy_canvas = tk.Canvas(tab, height=80, bg="white")
        self.buddy_canvas.pack(fill=tk.X, padx=10, pady=10)

        # -------- Text View --------
        self.buddy_output = tk.Text(tab, height=12)
        self.buddy_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._refresh_buddy_view()

    def _buddy_malloc(self):
        val = self.buddy_alloc_entry.get().strip()
        if not val.isdigit():
            return

        size = int(val)
        self.stats.record_request()

        addr = self.buddy.malloc(size)

        if addr is not None:
            self.stats.record_success()
            order = self.buddy.used[addr]
            allocated_size = 1 << order
            self.stats.add_internal_fragmentation(allocated_size - size)
        else:
            self.stats.record_failure()

        self._refresh_buddy_view()

    def _buddy_free(self):
        if self.buddy_free_entry.get().isdigit():
            self.buddy.free_block(int(self.buddy_free_entry.get()))
            self._refresh_buddy_view()

    def _refresh_buddy_view(self):
        # -------- Text --------
        self.buddy_output.delete("1.0", tk.END)

        self.buddy_output.insert(tk.END, "Allocated Blocks:\n")
        if not self.buddy.used:
            self.buddy_output.insert(tk.END, "  (none)\n")
        else:
            for addr, order in sorted(self.buddy.used.items()):
                self.buddy_output.insert(
                    tk.END, f"  Addr {addr}, size {1 << order}\n"
                )

        self.buddy_output.insert(tk.END, "\nFree Lists:\n")
        for o in range(self.buddy.max_order + 1):
            self.buddy_output.insert(
                tk.END, f"Order {o} (size {1 << o}): {self.buddy.free[o]}\n"
            )

        # -------- Visual --------
        self._draw_buddy_bar()
        self._refresh_stats_view()

    def _draw_buddy_bar(self):
        self.buddy_canvas.delete("all")

        total_mem = self.buddy.size
        canvas_width = self.buddy_canvas.winfo_width()

        if canvas_width <= 1:
            self.root.after(100, self._draw_buddy_bar)
            return

        segments = []

        # Allocated blocks
        for addr, order in self.buddy.used.items():
            segments.append((addr, 1 << order, False))

        # Free blocks
        for order, addrs in self.buddy.free.items():
            for addr in addrs:
                segments.append((addr, 1 << order, True))

        segments.sort(key=lambda x: x[0])

        x = 0
        for addr, size, is_free in segments:
            width = (size / total_mem) * canvas_width
            color = "#6ab04c" if is_free else "#eb4d4b"

            self.buddy_canvas.create_rectangle(
                x, 10, x + width, 70, fill=color, outline="black"
            )

            label = f"{size}"
            self.buddy_canvas.create_text(
                x + width / 2, 40, text=label, font=("Arial", 9)
            )

            x += width

    # ==========================================================
    # CACHE TAB (STANDALONE)
    # ==========================================================
    def _build_cache_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Cache Simulator")

        top = ttk.Frame(tab)
        top.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top, text="Physical Address:").pack(side=tk.LEFT)
        self.cache_entry = ttk.Entry(top, width=10)
        self.cache_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(top, text="Access", command=self._cache_access_ui).pack(side=tk.LEFT)

        self.cache_output = tk.Text(tab)
        self.cache_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._refresh_cache_view()

    def _cache_access_ui(self):
        if not self.cache_entry.get().isdigit():
            return

        addr = int(self.cache_entry.get())
        result = self.l1_cache.access(addr)
        self.last_cache_access["L1"] = result

        if not result["hit"]:
            result2 = self.l2_cache.access(addr)
            self.last_cache_access["L2"] = result2
        else:
            self.last_cache_access["L2"] = None

        self._refresh_cache_view()

    def _refresh_cache_view(self):
        self.cache_output.delete("1.0", tk.END)

        for cache in (self.l1_cache, self.l2_cache):
            self.cache_output.insert(
                tk.END,
                f"{cache.name} Cache (Hits={cache.hits}, Misses={cache.misses})\n"
            )

            last = self.last_cache_access.get(cache.name)

            for i, cache_set in enumerate(cache.sets):
                line = f"  Set {i}: "

                for idx, cl in enumerate(cache_set):
                    if cl.valid:
                        box = f"[{cl.tag}]"
                    else:
                        box = "[ - ]"

                    # Highlight accessed set
                    if last and last["set"] == i:
                        box = f"*{box}*"

                    # Highlight eviction
                    if last and last["set"] == i and last["evicted"]:
                        box = f"!{box}!"

                    line += box + " "

                self.cache_output.insert(tk.END, line + "\n")

            self.cache_output.insert(tk.END, "\n")

    # ==========================================================
    # VIRTUAL MEMORY TAB (INTEGRATED)
    # ==========================================================
    def _build_vm_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Virtual Memory")

        top = ttk.Frame(tab)
        top.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top, text="Virtual Address:").pack(side=tk.LEFT)
        self.vm_addr_entry = ttk.Entry(top, width=10)
        self.vm_addr_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(top, text="Access", command=self._vm_access_ui).pack(side=tk.LEFT)

        self.vm_output = tk.Text(tab)
        self.vm_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._refresh_vm_view()

    def _vm_access_ui(self):
        if not self.vm_addr_entry.get().isdigit():
            return

        result = self._integrated_access(int(self.vm_addr_entry.get()))
        self._refresh_vm_view(result)

    def _refresh_vm_view(self, last=None):
        self.vm_output.delete("1.0", tk.END)

        if last:
            self.vm_output.insert(
                tk.END,
                "Integrated Access Trace:\n"
                f"  Virtual Address : {last['va']}\n"
                f"  Page Number     : {last['page']}\n"
                f"  Offset          : {last['offset']}\n"
                f"  Frame Number    : {last['frame']}\n"
                f"  Physical Address: {last['pa']}\n"
                f"  Page Fault      : {'YES' if last['page_fault'] else 'NO'}\n"
                f"  Cache Result    : {last['cache_result']}\n\n"
            )

        self.vm_output.insert(
            tk.END, f"Total Page Faults: {self.vm.page_faults}\n\n"
        )

        self.vm_output.insert(tk.END, "Page Table:\n")
        for p, e in sorted(self.vm.page_table.items()):
            self.vm_output.insert(
                tk.END,
                f"  Page {p}: {'VALID' if e.valid else 'INVALID'}, Frame {e.frame}\n"
            )

        self.vm_output.insert(tk.END, "\nPhysical Frames:\n")
        for i, p in enumerate(self.vm.frames):
            self.vm_output.insert(
                tk.END, f"  Frame {i}: {'Page ' + str(p) if p is not None else 'FREE'}\n"
            )

    # ==========================================================
    # STATS TAB
    # ==========================================================
    def _build_stats_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stats / Graphs")

        self.stats_output = tk.Text(tab)
        self.stats_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._refresh_stats_view()

    def _refresh_stats_view(self):
        # Guard: stats tab not built yet
        if not hasattr(self, "stats_output"):
            return

        self.stats_output.delete("1.0", tk.END)

        used_mem = self._physical_used_memory()
        utilization = self.stats.memory_utilization(used_mem)
        ext_frag = fragmentation(self.memory.blocks)

        self.stats_output.insert(
            tk.END,
            "=== Allocation Statistics ===\n"
            f"Total Requests         : {self.stats.total_requests}\n"
            f"Successful Allocations : {self.stats.successful_allocations}\n"
            f"Failed Allocations     : {self.stats.failed_allocations}\n"
            f"Success Rate           : {self.stats.success_rate() * 100:.2f}%\n"
            f"Failure Rate           : {self.stats.failure_rate() * 100:.2f}%\n\n"
        )

        self.stats_output.insert(
            tk.END,
            "=== Memory Statistics (Physical Memory) ===\n"
            f"Total Memory           : {self.memory.size}\n"
            f"Used Memory            : {used_mem}\n"
            f"Memory Utilization     : {utilization * 100:.2f}%\n"
            f"External Fragmentation : {ext_frag * 100:.2f}%\n\n"
        )

        self.stats_output.insert(
            tk.END,
            "=== Buddy Allocator Statistics ===\n"
            f"Internal Fragmentation (bytes): {self.stats.internal_fragmentation}\n"
        )

    def run(self):
        self.root.mainloop()
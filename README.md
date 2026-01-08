# Memory Management Simulator

A Python-based Memory Management Simulator with a Tkinter graphical interface that models core operating system memory-management concepts such as dynamic memory allocation, fragmentation, caching, and virtual memory.

This project is a simulation designed for educational purposes. It demonstrates how operating systems manage memory internally using well-defined algorithms and data structures.

---

## Features

### Physical Memory Simulation
- Simulates a contiguous block of physical memory
- Dynamic splitting and merging of memory blocks
- Explicit tracking of allocated and free regions

### Memory Allocation Strategies
Implemented allocation algorithms:
- First Fit
- Best Fit
- Worst Fit

Each allocation request:
- Searches for a suitable free memory block
- Splits blocks if required

Each deallocation request:
- Frees the allocated block
- Coalesces adjacent free blocks to reduce fragmentation

### Visualization
- Graphical memory layout using Tkinter
- Color-coded representation of memory blocks
- Real-time updates after allocation and deallocation

### Metrics and Statistics
- Total memory
- Used memory
- Memory utilization
- External fragmentation
- Allocation success and failure count

### Extendable Components
- Buddy Memory Allocation (optional)
- Multilevel Cache Simulation (L1/L2)
- Cache replacement policies (FIFO, LRU)
- Virtual Memory using paging
- Page replacement policies (FIFO, LRU)

---

## Project Structure

memory-simulator/
├── src/
│   ├── allocator/
│   │   ├── base_allocator.py
│   │   ├── first_fit.py
│   │   ├── best_fit.py
│   │   └── worst_fit.py
│   │
│   ├── buddy/
│   │   └── buddy_allocator.py
│   │
│   ├── cache/
│   │   ├── cache_base.py
│   │   ├── fifo_cache.py
│   │   └── lru_cache.py
│   │
│   ├── virtual_memory/
│   │   ├── page_table.py
│   │   └── paging_system.py
│   │
│   ├── memory.py
│   ├── stats.py
│   ├── ui.py
│   └── main.py
│
├── tests/
├── docs/
├── README.md
└── requirements.txt


---

## How to Run

### Prerequisites
- Python 3.8 or higher
- Tkinter (included with standard Python installations)

### Running the Simulator
```bash
python src/main.py

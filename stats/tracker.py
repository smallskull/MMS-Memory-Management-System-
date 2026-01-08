class StatsTracker:
    def __init__(self, total_memory):
        self.total_memory = total_memory

        # Allocation stats
        self.total_requests = 0
        self.successful_allocations = 0
        self.failed_allocations = 0

        # Fragmentation
        self.internal_fragmentation = 0  # buddy only (bytes)

    # ---------- Allocation ----------
    def record_request(self):
        self.total_requests += 1

    def record_success(self):
        self.successful_allocations += 1

    def record_failure(self):
        self.failed_allocations += 1

    # ---------- Internal Fragmentation ----------
    def add_internal_fragmentation(self, wasted_bytes):
        if wasted_bytes > 0:
            self.internal_fragmentation += wasted_bytes

    # ---------- Derived Metrics ----------
    def success_rate(self):
        if self.total_requests == 0:
            return 0.0
        return self.successful_allocations / self.total_requests

    def failure_rate(self):
        if self.total_requests == 0:
            return 0.0
        return self.failed_allocations / self.total_requests

    def memory_utilization(self, used_memory):
        if self.total_memory == 0:
            return 0.0
        return used_memory / self.total_memory

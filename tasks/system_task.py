"""
System Monitoring Task for KashtawaOS
"""

import time
import gc

class SystemTask:
    """Monitors system health and resources"""
    
    def __init__(self):
        """Initialize system monitor"""
        self.start_time = time.ticks_ms()
        self.tick_count = 0
    
    def monitor(self):
        """Monitor system status (non-blocking)"""
        self.tick_count += 1
        uptime_sec = time.ticks_diff(time.ticks_ms(), self.start_time) // 1000
        mem_free = gc.mem_free()
        
        # Print every 10 ticks to avoid console spam
        if self.tick_count % 10 == 0:
            print(f"[System] Uptime: {uptime_sec}s | Free memory: {mem_free} bytes")
        
        # Collect garbage periodically
        if self.tick_count % 50 == 0:
            gc.collect()

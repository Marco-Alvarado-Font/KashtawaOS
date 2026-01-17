"""
Simple Task class for KashtawaOS RTOS
"""

import time

class Task:
    """Lightweight task for cooperative multitasking"""
    
    def __init__(self, name, func, interval_ms=100):
        """
        Create a new task
        
        Args:
            name: Task name
            func: Function to execute (should be non-blocking)
            interval_ms: Execution interval in milliseconds
        """
        self.name = name
        self.func = func
        self.interval_ms = interval_ms
        self.last_run = 0
        self.enabled = True
    
    def should_run(self):
        """Check if task should run based on interval"""
        if not self.enabled:
            return False
        
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_run) >= self.interval_ms:
            return True
        return False
    
    def run(self):
        """Execute the task function"""
        if self.should_run():
            try:
                self.func()
                self.last_run = time.ticks_ms()
            except Exception as e:
                print(f"Task {self.name} error: {e}")
    
    def enable(self):
        """Enable task execution"""
        self.enabled = True
    
    def disable(self):
        """Disable task execution"""
        self.enabled = False

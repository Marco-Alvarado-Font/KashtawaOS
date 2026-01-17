"""
Simple Cooperative Scheduler for KashtawaOS RTOS
"""

import time
from .task import Task

class Scheduler:
    """Simple round-robin cooperative task scheduler"""
    
    def __init__(self):
        """Initialize the scheduler"""
        self.tasks = []
        self.running = False
    
    def add_task(self, task):
        """Add a task to the scheduler"""
        self.tasks.append(task)
        print(f"Task added: {task.name} (interval: {task.interval_ms}ms)")
    
    def create_task(self, name, func, interval_ms=100):
        """Create and add a new task"""
        task = Task(name, func, interval_ms)
        self.add_task(task)
        return task
    
    def run(self):
        """Start the scheduler - runs forever"""
        print("=== Scheduler Starting ===")
        print(f"Total tasks: {len(self.tasks)}")
        self.running = True
        
        while self.running:
            # Run each task that's ready
            for task in self.tasks:
                task.run()
            
            # Small yield to prevent CPU hogging
            time.sleep_ms(1)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        print("Scheduler stopped")

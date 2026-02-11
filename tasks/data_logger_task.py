"""
Data Logger Task for KashtawaOS
Logs sensor data to internal flash storage in JSON format
"""

import time
import gc

class DataLoggerTask:
    """Task for logging sensor data to internal flash storage"""
    
    def __init__(self, storage_driver, sensor_task, id_lector="000001", id_antena="000001"):
        """
        Initialize data logger task
        
        Args:
            storage_driver: InternalStorageDriver instance
            sensor_task: SensorTask instance to read data from
            id_lector: ID del lector RFID (default: "000001")
            id_antena: ID de la antena (default: "000001")
        """
        self.storage = storage_driver
        self.sensor_task = sensor_task
        self.id_lector = id_lector
        self.id_antena = id_antena
        self.placa = "000001"      # Fixed plate ID
        self.potencia = "000040"   # Fixed power value
        self.log_count = 0
        self.initialized = False
        
    def initialize_log(self):
        """Initialize log file"""
        try:
            if self.storage.file_exists():
                # File exists, show stats
                lines = self.storage.get_line_count()
                size_kb = self.storage.get_file_size() / 1024
                print(f"[Logger] Existing log file found: {lines} entries, {size_kb:.2f} KB")
            else:
                print(f"[Logger] Creating new log file: {self.storage.log_file}")
                
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"[Logger] Initialization error: {e}")
            return False
            
    def log_data(self):
        """Log sensor data to internal flash in JSON format"""
        try:
            # Initialize log file if needed
            if not self.initialized:
                if not self.initialize_log():
                    print("[Logger] Failed to initialize, skipping log")
                    return
                    
            # Get sensor data (in centimeters)
            distance_cm = self.sensor_task.last_distance
            has_error = self.sensor_task.has_error
            
            # Convert to meters and handle errors
            if has_error:
                altura_metros = 0.0
            else:
                altura_metros = round(distance_cm / 100.0, 3)  # Convert cm to meters
            
            # Create JSON object with compact formatting (no spaces after colons)
            data = {
                "Id_lector": self.id_lector,
                "id_antena": self.id_antena,
                "placa": self.placa,
                "potencia": self.potencia,
                "altura": altura_metros
            }
            
            # Debug: Show what we're trying to write
            print(f"[Logger] Writing entry {self.log_count + 1}: {altura_metros}m (from {distance_cm:.2f}cm)")
            
            # Write JSON to internal flash
            if self.storage.write_json(data):
                self.log_count += 1
                print(f"[Logger] ✓ Entry {self.log_count} saved successfully")
                
                # Print progress every 10 entries
                if self.log_count % 10 == 0:
                    size_kb = self.storage.get_file_size() / 1024
                    print(f"[Logger] === Logged {self.log_count} entries ({size_kb:.2f} KB) ===")
            else:
                print("[Logger] ✗ Failed to write entry")
                
            # Collect garbage to free memory
            gc.collect()
            
        except Exception as e:
            print(f"[Logger] Error logging data: {e}")
            
    def get_log_stats(self):
        """
        Get logging statistics
        
        Returns:
            Dictionary with log statistics
        """
        try:
            file_size = self.storage.get_file_size()
            line_count = self.storage.get_line_count()
            
            return {
                'log_count': self.log_count,
                'file_size': file_size,
                'file_size_kb': file_size / 1024,
                'line_count': line_count,
                'file_exists': self.storage.file_exists(),
                'filename': self.storage.log_file
            }
        except Exception as e:
            print(f"[Logger] Stats error: {e}")
            return None
    
    def clear_log(self):
        """
        Clear all log data and reset counters
        
        Returns:
            True if successful, False otherwise
        """
        if self.storage.clear_file():
            self.log_count = 0
            self.initialized = False
            print("[Logger] Log cleared successfully")
            return True
        return False
    
    def read_log(self, max_lines=None):
        """
        Read log data
        
        Args:
            max_lines: Maximum number of lines to read (None for all)
            
        Returns:
            String with log contents
        """
        if max_lines:
            lines = self.storage.read_lines(max_lines)
            return ''.join(lines)
        else:
            return self.storage.read_all()
    
    def print_recent_logs(self, count=5):
        """
        Print the most recent log entries in JSON format
        
        Args:
            count: Number of recent entries to print
        """
        entries = self.storage.read_json_lines(count)
        if entries:
            print(f"[Logger] Last {len(entries)} entries:")
            for entry in entries:
                print(f"  {entry}")
        else:
            print("[Logger] No log data available")
    
    def set_ids(self, id_lector=None, id_antena=None):
        """
        Set the ID lector and ID antena
        
        Args:
            id_lector: New ID lector (None to keep current)
            id_antena: New ID antena (None to keep current)
        """
        if id_lector:
            self.id_lector = id_lector
            print(f"[Logger] ID Lector updated: {id_lector}")
        if id_antena:
            self.id_antena = id_antena
            print(f"[Logger] ID Antena updated: {id_antena}")

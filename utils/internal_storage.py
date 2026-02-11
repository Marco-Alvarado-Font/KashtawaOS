"""
Internal Storage Driver for Raspberry Pi Pico W
Handles file I/O operations on the internal flash filesystem
Supports JSON format for structured data logging
"""

import json

class InternalStorageDriver:
    """Driver for internal filesystem operations on Pico W flash"""
    
    def __init__(self, log_file="data.txt"):
        """
        Initialize internal storage driver
        
        Args:
            log_file: Name of the log file (default: data.txt)
        """
        self.log_file = log_file
        self.is_available = True
        print(f"[Storage] Internal storage initialized")
        print(f"[Storage] Log file: {self.log_file}")
    
    def write_line(self, data):
        """
        Write a line to the log file (appends to existing file)
        
        Args:
            data: String to write to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.log_file, "a") as f:
                f.write(data + "\n")
            return True
        except Exception as e:
            print(f"[Storage] Error writing to file: {e}")
            self.is_available = False
            return False
    
    def write_json(self, data_dict):
        """
        Write a JSON object to the log file (one JSON per line)
        Uses compact format without spaces after separators
        
        Args:
            data_dict: Dictionary to write as JSON
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use separators to remove spaces for compact format
            json_string = json.dumps(data_dict, separators=(',', ':'))
            with open(self.log_file, "a") as f:
                f.write(json_string + "\n")
            return True
        except Exception as e:
            print(f"[Storage] Error writing JSON: {e}")
            self.is_available = False
            return False
    
    def read_all(self):
        """
        Read all contents from the log file
        
        Returns:
            String with file contents, or empty string if file doesn't exist
        """
        try:
            with open(self.log_file, "r") as f:
                return f.read()
        except OSError:
            # File doesn't exist yet
            return ""
        except Exception as e:
            print(f"[Storage] Error reading file: {e}")
            return None
    
    def read_lines(self, max_lines=None):
        """
        Read lines from the log file
        
        Args:
            max_lines: Maximum number of lines to read (None for all)
            
        Returns:
            List of lines
        """
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                if max_lines:
                    return lines[-max_lines:]  # Return last N lines
                return lines
        except OSError:
            return []
        except Exception as e:
            print(f"[Storage] Error reading lines: {e}")
            return []
    
    def clear_file(self):
        """
        Clear the log file (delete all contents)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.log_file, "w") as f:
                f.write("")
            print(f"[Storage] Log file cleared: {self.log_file}")
            return True
        except Exception as e:
            print(f"[Storage] Error clearing file: {e}")
            return False
    
    def get_file_size(self):
        """
        Get the size of the log file in bytes
        
        Returns:
            File size in bytes, or 0 if file doesn't exist
        """
        try:
            import os
            stat = os.stat(self.log_file)
            return stat[6]  # Size is at index 6
        except:
            return 0
    
    def file_exists(self):
        """
        Check if the log file exists
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            import os
            os.stat(self.log_file)
            return True
        except:
            return False
    
    def get_line_count(self):
        """
        Count the number of lines in the log file
        
        Returns:
            Number of lines, or 0 if file doesn't exist
        """
        try:
            with open(self.log_file, "r") as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def read_json_lines(self, max_lines=None):
        """
        Read JSON objects from file (one JSON per line)
        
        Args:
            max_lines: Maximum number of lines to read (None for all)
            
        Returns:
            List of dictionaries
        """
        try:
            data_list = []
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                if max_lines:
                    lines = lines[-max_lines:]
                
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            data_list.append(json.loads(line))
                        except:
                            pass  # Skip invalid JSON lines
            return data_list
        except OSError:
            return []
        except Exception as e:
            print(f"[Storage] Error reading JSON: {e}")
            return []

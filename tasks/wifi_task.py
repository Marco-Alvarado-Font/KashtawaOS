"""
WiFi Task - Network connectivity management
Manages WiFi connection
"""

from utils.wifi_driver import WiFiDriver
import gc

class WiFiTask:
    """Task for WiFi connectivity"""
    
    def __init__(self, wifi_driver):
        """
        Initialize WiFi task
        
        Args:
            wifi_driver: WiFiDriver instance
        """
        self.wifi = wifi_driver
        self.connection_attempts = 0
        
    def connect_wifi(self):
        """Maintain WiFi connection (non-blocking check)"""
        try:
            if not self.wifi.is_connected():
                if self.connection_attempts == 0:
                    print("Connecting to WiFi: {}".format(self.wifi.ssid))
                    self.connection_attempts = 1
                    
                    # Attempt connection
                    if self.wifi.connect():
                        ip = self.wifi.get_ip()
                        print("WiFi Connected: {}".format(ip))
                    else:
                        print("WiFi: Connection failed, will retry...")
                        self.connection_attempts = 0
            else:
                # Already connected
                if self.connection_attempts != 0:
                    self.connection_attempts = 0
                    
            gc.collect()
            
        except Exception as e:
            print('WiFi task error:', e)
            self.connection_attempts = 0
            
    @property
    def connected(self):
        """Check if WiFi is connected"""
        return self.wifi.is_connected()

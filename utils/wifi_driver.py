"""
WiFi Driver for Raspberry Pi Pico W
Handles network connectivity
"""

import network
import time

# WiFi credentials
WIFI_SSID = 'Milky'
WIFI_PASSWORD = 'Milky1414'

class WiFiDriver:
    """WiFi driver for network operations"""
    
    def __init__(self):
        """Initialize WiFi driver"""
        self.ssid = WIFI_SSID
        self.password = WIFI_PASSWORD
        self.wlan = None
        self.connected = False
        
    def connect(self):
        """
        Attempt to connect to WiFi network
        Returns connection status
        """
        try:
            if self.wlan is None:
                self.wlan = network.WLAN(network.STA_IF)
                self.wlan.active(True)
                
            if not self.wlan.isconnected():
                self.wlan.connect(self.ssid, self.password)
                
                # Wait up to 10 seconds for connection
                max_wait = 10
                while max_wait > 0 and not self.wlan.isconnected():
                    time.sleep(1)
                    max_wait -= 1
                    
                if self.wlan.isconnected():
                    self.connected = True
                    return True
                else:
                    self.connected = False
                    return False
            else:
                self.connected = True
                return True
                
        except Exception as e:
            print('WiFi connection error:', e)
            self.connected = False
            return False
            
    def is_connected(self):
        """Check if WiFi is connected"""
        if self.wlan:
            self.connected = self.wlan.isconnected()
        return self.connected
        
    def get_ip(self):
        """Get IP address if connected"""
        if self.is_connected():
            return self.wlan.ifconfig()[0]
        return None
        
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.wlan:
            self.wlan.disconnect()
            self.connected = False

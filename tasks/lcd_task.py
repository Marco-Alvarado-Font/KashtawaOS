"""
LCD Display Task for KashtawaOS
Displays sensor data and system information
"""

class LCDTask:
    """Manages LCD display updates"""
    
    def __init__(self, lcd, sensor_task, wifi_task=None):
        """
        Initialize LCD task
        
        Args:
            lcd: I2cLcd instance
            sensor_task: SensorTask instance to read data from
            wifi_task: WiFiTask instance (optional) to display connection status
        """
        self.lcd = lcd
        self.sensor_task = sensor_task
        self.wifi_task = wifi_task
    
    def update_display(self):
        """Update LCD display with sensor data (non-blocking)"""
        try:
            # Clear the LCD
            self.lcd.clear()
            
            # Show distance
            self._show_distance()
                
        except Exception as e:
            print('LCD error:', e)
            
    def _show_distance(self):
        """Helper to show distance on LCD"""
        # Check if sensor has error
        if self.sensor_task.has_error:
            self.lcd.putstr("Sensor Error")
            self.lcd.move_to(0, 1)
            self.lcd.putstr("Out of range")
        else:
            # Display distance from sensor
            distance = self.sensor_task.last_distance
            
            # First line: Distance with WiFi status
            if self.wifi_task and self.wifi_task.connected:
                self.lcd.putstr('Dist: WiFi OK')
            else:
                self.lcd.putstr('Dist: No WiFi')
            
            # Second line: Distance value
            self.lcd.move_to(0, 1)
            self.lcd.putstr('{:.3f} cm      '.format(distance))


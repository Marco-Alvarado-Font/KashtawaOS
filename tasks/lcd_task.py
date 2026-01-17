"""
LCD Display Task for KashtawaOS
Displays sensor data and system information
"""

class LCDTask:
    """Manages LCD display updates"""
    
    def __init__(self, lcd, sensor_task):
        """
        Initialize LCD task
        
        Args:
            lcd: I2cLcd instance
            sensor_task: SensorTask instance to read data from
        """
        self.lcd = lcd
        self.sensor_task = sensor_task
        self.counter = 0
    
    def update_display(self):
        """Update LCD display with sensor data (non-blocking)"""
        try:
            # Clear the LCD
            self.lcd.clear()
            
            # Check if sensor has error
            if self.sensor_task.has_error:
                self.lcd.putstr("Sensor Error")
                self.lcd.move_to(0, 1)
                self.lcd.putstr("Out of range")
            else:
                # Display distance from sensor
                distance = self.sensor_task.last_distance
                self.lcd.putstr('Distance: {} cm'.format(distance))
                
        except Exception as e:
            print('LCD error:', e)

"""
Sensor Task - HC-SR04 Ultrasonic Distance Sensor
Reads distance measurements and stores data
"""

import gc

class SensorTask:
    """Task for reading HC-SR04 ultrasonic sensor"""
    
    def __init__(self, sensor):
        """
        Initialize sensor task
        
        Args:
            sensor: HCSR04 sensor instance
        """
        self.sensor = sensor
        self.last_distance = 0
        self.error_count = 0
        self.has_error = False
        
    def read_distance(self):
        """Read distance from sensor (non-blocking)"""
        try:
            # Measure distance in centimeters
            distance_cm = self.sensor.distance_cm()
            self.last_distance = distance_cm
            self.error_count = 0
            self.has_error = False
            
            print('Distance: {} cm'.format(distance_cm))
            
            # Memory management
            gc.collect()
            
        except OSError as e:
            self.error_count += 1
            self.has_error = True
            print('Sensor error:', e)
            
        except Exception as e:
            self.has_error = True
            print('Unexpected error:', e)

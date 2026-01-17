"""
KashtawaRTOS - Simple RTOS for Raspberry Pi Pico W
Real-Time Operating System for autonomous inventory control drone
"""

from machine import Pin, SoftI2C
import time
from utils.pico_i2c_lcd import I2cLcd
from utils.hcsr04 import HCSR04
from core.scheduler import Scheduler
from tasks.sensor_task import SensorTask
from tasks.lcd_task import LCDTask
from tasks.system_task import SystemTask

def main():
    """Main system function - Initialize RTOS and start scheduler"""
    print("===  KashtawaRTOS v1.0      ===")
    print("Autonomous Inventory Control Drone")
    print("Simple Real-Time Operating System")
    print("")
    
    # Hardware configuration
    I2C_ADDR = 0x27
    I2C_NUM_ROWS = 2
    I2C_NUM_COLS = 16
    HC_TRIGGER_PIN = 27
    HC_ECHO_PIN = 28
    
    # Initialize hardware
    print("Initializing hardware...")
    try:
        # Initialize I2C LCD
        i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
        lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
        
        # Initialize HC-SR04 ultrasonic sensor
        sensor = HCSR04(trigger_pin=HC_TRIGGER_PIN, echo_pin=HC_ECHO_PIN, echo_timeout_us=30000)
        
        # Startup message
        lcd.clear()
        lcd.putstr("KashtawaRTOS v1.0")
        lcd.move_to(0, 1)
        lcd.putstr("RTOS Starting...")
        time.sleep(2)
        
        print("Hardware initialized successfully")
        print(f"  - LCD: I2C @ 0x{I2C_ADDR:02X}")
        print(f"  - HC-SR04: Trigger=GPIO{HC_TRIGGER_PIN}, Echo=GPIO{HC_ECHO_PIN}")
        
    except Exception as e:
        print(f"Error initializing hardware: {e}")
        return
    
    # Create RTOS scheduler
    print("")
    print("Creating RTOS scheduler...")
    scheduler = Scheduler()
    
    # Create task objects
    sensor_task = SensorTask(sensor)
    lcd_task = LCDTask(lcd, sensor_task)
    system_task = SystemTask()
    
    # Add tasks to scheduler
    # Distance measurement every 2 seconds (slower for stable readings)
    scheduler.create_task("Distance Sensor", sensor_task.read_distance, interval_ms=2000)
    
    # LCD update every 2 seconds (synchronized with sensor)
    scheduler.create_task("LCD Display", lcd_task.update_display, interval_ms=2000)
    
    # System monitor every 10 seconds (low priority)
    scheduler.create_task("System Monitor", system_task.monitor, interval_ms=10000)
    
    # Start the RTOS scheduler (runs forever)
    print("")
    print("Starting scheduler...")
    print("Tasks registered:")
    print("  - Distance Sensor: 2000ms interval")
    print("  - LCD Display: 2000ms interval")
    print("  - System Monitor: 10000ms interval")
    print("")
    
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        lcd.clear()
        lcd.putstr("System Stopped")

# Auto-execution on power-up
if __name__ == "__main__":
    main()
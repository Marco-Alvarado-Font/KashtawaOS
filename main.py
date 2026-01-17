"""
KashtawaOS - Simple RTOS for Raspberry Pi Pico W
Real-Time Operating System for autonomous inventory control drone
"""

from machine import Pin, SoftI2C
import time
from utils.pico_i2c_lcd import I2cLcd
from core.scheduler import Scheduler
from tasks.lcd_task import LCDTask
from tasks.system_task import SystemTask

def main():
    """Main system function - Initialize RTOS and start scheduler"""
    print("=== KashtawaOS v1.0 - RTOS Edition ===")
    print("Autonomous Inventory Control Drone")
    print("Simple Real-Time Operating System")
    print("")
    
    # Hardware configuration
    I2C_ADDR = 0x27
    I2C_NUM_ROWS = 2
    I2C_NUM_COLS = 16
    
    # Initialize hardware
    print("Initializing hardware...")
    try:
        i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
        lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
        
        # Startup message
        lcd.clear()
        lcd.putstr("KashtawaOS v2.0")
        lcd.move_to(0, 1)
        lcd.putstr("RTOS Starting...")
        time.sleep(2)
        
        print("Hardware initialized successfully")
        
    except Exception as e:
        print(f"Error initializing hardware: {e}")
        return
    
    # Create RTOS scheduler
    print("")
    print("Creating RTOS scheduler...")
    scheduler = Scheduler()
    
    # Create task objects
    lcd_task = LCDTask(lcd)
    system_task = SystemTask()
    
    # Add tasks to scheduler
    # LCD updates every 2 seconds
    scheduler.create_task("LCD Display", lcd_task.update_display, interval_ms=2000)
    
    # System monitor every 5 seconds
    scheduler.create_task("System Monitor", system_task.monitor, interval_ms=5000)
    
    # Start the RTOS scheduler (runs forever)
    print("")
    print("Starting scheduler...")
    lcd.clear()
    lcd.putstr("RTOS Running")
    time.sleep(1)
    
    scheduler.run()

# Auto-execution on power-up
if __name__ == "__main__":
    main()
"""
LCD Display Task for KashtawaOS
"""

class LCDTask:
    """Manages LCD display updates"""
    
    def __init__(self, lcd):
        """
        Initialize LCD task
        
        Args:
            lcd: I2cLcd instance
        """
        self.lcd = lcd
        self.message_line1 = "KashtawaOS"
        self.message_line2 = "Ready"
        self.counter = 0
    
    def update_display(self):
        """Update LCD display (non-blocking)"""
        try:
            self.lcd.clear()
            self.lcd.putstr(self.message_line1)
            self.lcd.move_to(0, 1)
            self.lcd.putstr(f"{self.message_line2} {self.counter}")
            self.counter += 1
        except Exception as e:
            print(f"LCD error: {e}")
    
    def set_message(self, line1, line2=""):
        """Set custom message to display"""
        self.message_line1 = line1[:16]  # Max 16 chars
        self.message_line2 = line2[:16]

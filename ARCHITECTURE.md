# KashtawaRTOS - RTOS Architecture Documentation

## Overview

KashtawaRTOS is a simple cooperative Real-Time Operating System (RTOS) designed for the Raspberry Pi Pico W. It provides multitasking capabilities for autonomous inventory control drone applications.

**Version:** 1.0  
**Target Hardware:** Raspberry Pi Pico W (RP2040)  
**Language:** MicroPython  
**Type:** Cooperative (Non-preemptive) RTOS

---

## System Architecture

### 1. Core Components

#### 1.1 Scheduler (`core/scheduler.py`)
The heart of the RTOS. Implements a round-robin cooperative scheduler.

**Key Features:**
- Task registration and management
- Round-robin task execution
- Time-based task scheduling
- Non-blocking operation

**Main Methods:**
```python
add_task(task)              # Add existing task to scheduler
create_task(name, func, interval_ms)  # Create and register new task
run()                       # Start scheduler (infinite loop)
stop()                      # Stop scheduler execution
```

**Scheduling Algorithm:**
- Each task is checked in round-robin fashion
- Tasks execute only when their interval has elapsed
- Small 1ms sleep between iterations to prevent CPU hogging
- Cooperative - tasks must return control voluntarily

#### 1.2 Task (`core/task.py`)
Base task implementation for the RTOS.

**Properties:**
- `name` - Task identifier
- `func` - Function to execute
- `interval_ms` - Execution interval in milliseconds
- `last_run` - Timestamp of last execution
- `enabled` - Task enable/disable flag

**Key Methods:**
```python
should_run()    # Check if task interval has elapsed
run()          # Execute task function
enable()       # Enable task execution
disable()      # Disable task execution
```

**Timing Mechanism:**
- Uses `time.ticks_ms()` for millisecond precision
- Uses `time.ticks_diff()` for overflow-safe comparisons
- Non-blocking - only executes when interval expires

---

### 2. Task Implementations

#### 2.1 SensorTask (`tasks/sensor_task.py`)
Responsible for reading HC-SR04 ultrasonic distance sensor.

**Responsibilities:**
- Measure distance from HC-SR04 sensor
- Store last valid measurement
- Track error state
- Memory management (garbage collection)

**Data Flow:**
```
HC-SR04 Sensor → SensorTask.read_distance() → self.last_distance
                                            → self.has_error
```

**Error Handling:**
- Catches `OSError` for out-of-range measurements
- Sets `has_error` flag when measurement fails
- Continues operation without crashing

**Execution Interval:** 2000ms (2 seconds)

#### 2.2 LCDTask (`tasks/lcd_task.py`)
Handles all LCD display operations.

**Responsibilities:**
- Read sensor data from SensorTask
- Format and display distance on LCD
- Display error messages
- Manage LCD hardware

**Data Flow:**
```
SensorTask.last_distance → LCDTask.update_display() → LCD Hardware
SensorTask.has_error     ↗
```

**Display Format:**
- Line 1: "Distance:"
- Line 2: "XXX.XXX cm" (3 decimal places)
- Error: "Sensor Error" / "Out of range"

**Execution Interval:** 2000ms (2 seconds, synchronized with sensor)

#### 2.3 SystemTask (`tasks/system_task.py`)
Monitors system health and resources.

**Responsibilities:**
- Track system uptime
- Monitor free memory
- Periodic garbage collection
- System diagnostics

**Metrics:**
- Uptime in seconds
- Free memory in bytes
- Tick counter

**Execution Interval:** 10000ms (10 seconds, low priority)

#### 2.4 DataLoggerTask (`tasks/data_logger_task.py`)
Responsible for persistent logging of sensor data to internal flash storage.

**Responsibilities:**
- Read distance measurements from SensorTask
- Convert distance from cm to meters
- Format data as JSON with metadata
- Write to internal flash storage (data.txt)
- Ensure data persistence across reboots

**Data Flow:**
```
SensorTask.last_distance → DataLoggerTask.log_data() → InternalStorageDriver → Flash (data.txt)
```

**Log Format:**
```json
{"timestamp": 1234567890, "sensor_id": 1, "distance_m": 1.234, "type": "distance"}
```

**Features:**
- JSON Lines format (one JSON object per line)
- Automatic file append mode
- Explicit flush after each write for persistence
- Error handling with status tracking
- Debug output for verification

**Execution Interval:** 5000ms (5 seconds)

#### 2.5 ApiSyncTask (`tasks/api_sync_task.py`)
Responsible for synchronizing logged data with remote API server.

**Responsibilities:**
- Monitor accumulated data in internal storage
- Check WiFi connectivity status
- Send data batches to remote API
- Track synchronization statistics
- Handle network errors gracefully

**Data Flow:**
```
InternalStorageDriver → ApiSyncTask.check_and_send() → HTTP POST → Remote API
```

**API Configuration:**
```
Endpoint: https://www.fontsistemascr.com/.../api/RFID/RegisterTagRead
Method: POST
Authentication: X-API-Key header
```

**Features:**
- Batch sending (default: 10 readings per batch)
- Automatic WiFi connectivity check
- Retry logic for failed requests
- Statistics tracking (sent, pending, errors)
- Manual force sync capability

**Execution Interval:** 60000ms (60 seconds)

---

### 3. Hardware Drivers

#### 3.1 LCD Driver (`utils/pico_i2c_lcd.py`, `utils/lcd_api.py`)
I2C LCD display driver for HD44780-compatible displays via PCF8574.

**Hardware Configuration:**
- Interface: I2C (SoftI2C)
- Address: 0x27 (configurable)
- Display: 16x2 characters
- Pins: SDA=GPIO4, SCL=GPIO5

**Key Features:**
- Character display with cursor control
- Backlight control
- Custom character support
- Hardware abstraction layer

#### 3.2 HC-SR04 Driver (`utils/hcsr04.py`)
Ultrasonic distance sensor driver.

**Hardware Configuration:**
- Trigger Pin: GPIO 27
- Echo Pin: GPIO 28
- Timeout: 30000µs
- Range: 2cm - 4m

**Measurement Method:**
- Sends 10µs trigger pulse
- Measures echo pulse duration
- Calculates distance using sound speed (343.2 m/s)
- Returns distance in centimeters

#### 3.3 Internal Storage Driver (`utils/internal_storage.py`)
File I/O driver for persistent data storage on Pico W internal flash.

**Storage Configuration:**
- Filesystem: LittleFS (MicroPython default)
- Log File: data.txt (configurable)
- Format: JSON Lines (one JSON object per line)
- Mode: Append (preserves existing data)

**Key Features:**
- **Persistent Storage**: Data survives reboots and power cycles
- **JSON Support**: Structured data with compact formatting
- **Append Mode**: Accumulates data without overwriting
- **Explicit Flush**: Guarantees immediate write to flash
- **File Management**: Read, clear, and analyze log files

**Main Methods:**
```python
write_json(data_dict)           # Write JSON object to file
read_json_lines(max_lines)      # Read JSON objects from file
read_all()                      # Read entire file contents
clear_file()                    # Delete all log data
get_file_size()                 # Get file size in bytes
get_line_count()                # Count log entries
file_exists()                   # Check if log file exists
```

**Storage Characteristics:**
- No external hardware required (uses internal flash)
- Approximately 1.4MB available for user data
- Wear leveling handled by LittleFS
- Atomic writes for data integrity

---

## System Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   KashtawaRTOS RTOS                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │           Scheduler (Core)                     │      │
│  │  - Round-robin task execution                  │      │
│  │  - Time-based scheduling                       │      │
│  │  - Task management                             │      │
│  └──┬────┬───────┬────────┬─────────┬─────────────┘      │
│     │    │       │        │         │                    │
│  ┌──▼─┐ ┌▼────┐ ┌▼─────┐ ┌▼──────┐ ┌▼────────┐           │
│  │Sen │ │LCD  │ │Data  │ │System │ │API Sync │           │
│  │sor │ │Task │ │Logger│ │Task   │ │Task     │           │
│  │(2s)│ │(2s) │ │(5s)  │ │(10s)  │ │(60s)    │           │
│  └─┬──┘ └─┬───┘ └──┬───┘ └───────┘ └────┬────┘           │
│    │      │        │                     │               │
├────┼──────┼────────┼─────────────────────┼───────────────┤
│  Hardware Abstraction Layer              │               │
├────┼──────┼────────┼─────────────────────┼───────────────┤
│    │      │        │                     │               │
│  ┌─▼─┐ ┌──▼──┐ ┌───▼────────┐      ┌────▼────────┐       │
│  │HC │ │ LCD │ │ Internal   │      │ WiFi/HTTP   │       │
│  │SR │ │ I2C │ │ Storage    │      │ urequests   │       │ 
│  │04 │ │     │ │ (Flash)    │      │             │       │
│  └───┘ └─────┘ └────────────┘      └─────────────┘       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Task Scheduling Timeline

```
Time (ms)    0     2000    4000    5000    6000    10000   12000   15000   60000
             │      │       │       │       │       │       │       │       │
SensorTask   ●──────●───────●───────────────●───────●───────●───────●───────●
             │      │       │       │       │       │       │       │       │
LCDTask      ●──────●───────●───────────────●───────●───────●───────●───────●
             │      │       │       │       │       │       │       │       │
DataLogger   ●──────────────────────●───────────────────────●───────────────●
             │      │       │       │       │       │       │       │       │
SystemTask   ●──────────────────────────────●───────────────────────────────●
             │      │       │       │       │       │       │       │       │
ApiSyncTask  ●─────────────────────────────────────────────────────────────●

Legend:
● = Task execution
─ = Idle/waiting
```

---

## Memory Architecture

### Task Stack
Each task maintains minimal state:
- Task object: ~200 bytes
- Function reference: ~50 bytes
- Timing data: ~20 bytes

### Heap Management
- Automatic garbage collection after each task execution
- Manual garbage collection in SystemTask every 10 seconds
- MicroPython manages memory allocation

### Total RAM Usage (Estimated)
- Core RTOS: ~2 KB
- Tasks (5): ~2 KB
- Drivers: ~5 KB
- User data: ~2 KB
- Network buffers: ~5 KB
- **Total: ~16 KB** (RP2040 has 264 KB SRAM)

### Flash Storage Usage
- MicroPython firmware: ~1.4 MB
- User code (RTOS + tasks): ~20 KB
- Available for data logging: ~1.4 MB
- Log file format: ~80-100 bytes per entry (JSON)
- Estimated capacity: ~14,000-17,000 log entries

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Data Flow Diagram                    │
└─────────────────────────────────────────────────────────┘

  HC-SR04 Sensor                                    LCD Display
       │                                                 ▲
       │ Ultrasonic                                      │ I2C
       │ Pulse                                           │ Commands
       ▼                                                 │
┌──────────────┐                                  ┌──────────────┐
│  SensorTask  │                                  │   LCDTask    │
│              │                                  │              │
│ .last_distance◄──────────Read Data──────────────│ .sensor_task │
│ .has_error   │                                  │              │
└──────┬───────┘                                  └──────────────┘
       │                                                 ▲
       │ Read Data                                       │
       ▼                                                 │
┌──────────────┐                                         │
│DataLoggerTask│                                         │
│              │                                         │
│  .storage    │                                         │
└──────┬───────┘                                         │
       │                                                 │
       │ Write JSON                                      │
       ▼                                                 │
┌──────────────┐                                         │
│InternalStore │                                         │
│   Driver     │                                         │
│              │                                         │
│  data.txt    │                                         │
└──────┬───────┘                                         │
       │                                                 │
       ▼                                                 │
  Flash Storage                                          │
       ▲                                                 │
       │                                                 │
       └─────────────Scheduled by Scheduler──────────────┘
                            │
                     ┌──────────────┐
                     │  Scheduler   │
                     │              │
                     │ Round-robin  │
                     │ Time-based   │
                     └──────────────┘
```

---

## Configuration Parameters

### Hardware Configuration
```python
I2C_ADDR = 0x27           # LCD I2C address
I2C_NUM_ROWS = 2          # LCD rows
I2C_NUM_COLS = 16         # LCD columns
HC_TRIGGER_PIN = 27       # HC-SR04 trigger pin
HC_ECHO_PIN = 28          # HC-SR04 echo pin
```

### Task Intervals
```python
SENSOR_INTERVAL = 2000    # Distance measurement (ms)
LCD_INTERVAL = 2000       # Display update (ms)
LOGGER_INTERVAL = 5000    # Data logging (ms)
API_SYNC_INTERVAL = 60000 # API synchronization (ms)
SYSTEM_INTERVAL = 10000   # System monitor (ms)
```

### Storage Configuration
```python
LOG_FILE = "data.txt"     # Data log filename
LOG_FORMAT = "json"       # JSON Lines format
WRITE_MODE = "append"     # Preserve existing data
```

### API Configuration
```python
API_URL = "https://www.fontsistemascr.com/.../api/RFID/RegisterTagRead"
API_KEY = "RfidDroneTest" # API authentication key
BATCH_SIZE = 10           # Readings per sync batch
```

### Timing Parameters
```python
SCHEDULER_SLEEP = 1       # Scheduler loop delay (ms)
ECHO_TIMEOUT = 30000      # HC-SR04 timeout (µs)
I2C_FREQ = 400000         # I2C bus frequency (Hz)
```

---

## Design Principles

### 1. Separation of Concerns
- **SensorTask**: Only reads sensor
- **LCDTask**: Only displays data
- **DataLoggerTask**: Only logs data to storage
- **ApiSyncTask**: Only syncs data to remote API
- **SystemTask**: Only monitors system
- Each task has a single, well-defined responsibility

### 2. Cooperative Multitasking
- Tasks must complete quickly and return control
- No blocking operations in tasks
- All delays handled by scheduler intervals

### 3. Non-Blocking I/O
- All hardware operations complete quickly
- No busy-wait loops
- Timeout mechanisms for hardware failures

### 4. Error Resilience
- Tasks catch and handle their own errors
- Error flags propagate between tasks
- System continues operation on task failure

### 5. Resource Efficiency
- Minimal memory overhead
- Explicit garbage collection
- No dynamic memory allocation in loops

### 6. Data Persistence
- Append-only log file for reliability
- Explicit flush after each write
- JSON format for structured data
- No external storage dependencies
- Data survives reboots and power cycles

---

## Extension Guide

### Adding a New Task

1. **Create Task Class** (`tasks/new_task.py`):
```python
class NewTask:
    def __init__(self, hardware):
        self.hardware = hardware
    
    def execute(self):
        # Non-blocking operation
        pass
```

2. **Register in `tasks/__init__.py`**:
```python
from .new_task import NewTask
__all__ = ['SensorTask', 'LCDTask', 'SystemTask', 'NewTask']
```

3. **Add to Scheduler** (`main.py`):
```python
new_task = NewTask(hardware)
scheduler.create_task("New Task", new_task.execute, interval_ms=1000)
```

### Adding New Hardware

1. Create driver in `utils/` directory
2. Initialize in `main.py` hardware section
3. Pass driver instance to appropriate task
4. Update task to use new hardware

---

## Performance Characteristics

### Timing Accuracy
- **Resolution**: 1ms (limited by scheduler loop)
- **Jitter**: ±1-5ms (depends on task execution time)
- **Precision**: Sufficient for sensor polling and display updates

### CPU Utilization
- **Idle**: ~95% (1ms sleep in scheduler)
- **Task execution**: ~5% (quick bursts)
- **Scalability**: Can handle 5-10 tasks before degradation

### Storage Performance
- **Write speed**: ~1-2ms per JSON entry
- **File operations**: Non-blocking at task level
- **Flash endurance**: ~100,000 write cycles per block
- **Expected lifespan**: Years with typical logging intervals
- **Data integrity**: LittleFS wear leveling and power-loss protection

### Network Performance
- **API request time**: ~200-500ms per reading (network dependent)
- **Batch send time**: ~5-10 seconds for 10 readings
- **Data overhead**: ~100 bytes per reading + HTTP headers
- **Daily traffic**: ~50-100 KB (with 5s logging interval)

### Response Time
- **Sensor reading**: 2000ms (configured interval)
- **Display update**: 2000ms (configured interval)
- **Data logging**: 5000ms (configured interval)
- **API sync**: 60000ms (configured interval)
- **Maximum latency**: Task interval + execution time

---

## Limitations

1. **No Priority System**: All tasks have equal priority / for the moment
2. **No Preemption**: Long-running tasks block others
3. **No Inter-task Communication**: Tasks share data via object references
4. **No Real-time Guarantees**: Timing depends on task cooperation
5. **Single Core**: Does not utilize RP2040's second core
6. **Limited Flash Space**: ~1.4MB available for data logging
7. **No Data Compression**: JSON format uses more space than binary
8. **Network Dependency**: API sync requires stable WiFi connection
9. **No Retry Logic**: Failed API requests are not automatically retried

---

## Future Improvements

1. **Priority-based Scheduling**: Add task priority levels
2. **Message Queues**: Implement FIFO queues for inter-task communication
3. **Event System**: Add event-driven task activation
4. **Semaphores**: Add synchronization primitives
5. **Dual-core Support**: Utilize RP2040's second core
6. **Watchdog Timer**: Add task timeout detection
7. **Performance Metrics**: Add task execution time tracking
8. **Data Compression**: Implement binary or compressed log formats
9. **Remote Data Access**: WiFi-based log file download
10. **Circular Buffer**: Automatic log rotation when storage fills
11. **Retry Mechanism**: Automatic retry for failed API requests
12. **Batch API Requests**: Send multiple readings in single HTTP request
13. **API Response Validation**: Verify server acknowledgment of data
14. **Offline Queue**: Smart queue management during WiFi outages

---

## File Structure

```
KashtawaOS/
├── main.py                    # Entry point and system initialization
├── core/
│   ├── __init__.py
│   ├── scheduler.py          # Task scheduler implementation
│   └── task.py               # Base task class
├── tasks/
│   ├── __init__.py
│   ├── sensor_task.py        # HC-SR04 sensor task
│   ├── lcd_task.py           # LCD display task
│   ├── data_logger_task.py   # Data logging task
│   ├── api_sync_task.py      # API synchronization task
│   └── system_task.py        # System monitoring task
├── utils/
│   ├── __init__.py
│   ├── hcsr04.py            # HC-SR04 driver
│   ├── pico_i2c_lcd.py      # I2C LCD driver
│   ├── lcd_api.py           # LCD API abstraction
│   └── internal_storage.py  # Internal flash storage driver
├── data.txt                  # Persistent log file (created at runtime)
├── README.md                 # Project documentation
└── ARCHITECTURE.md           # Architecture documentation
```

---

## References

- **MicroPython Documentation**: https://docs.micropython.org/
- **Raspberry Pi Pico W**: https://www.raspberrypi.com/products/raspberry-pi-pico/
- **HC-SR04 Datasheet**: Ultrasonic ranging module
- **HD44780 LCD Controller**: Standard character LCD interface
- **Cooperative RTOS**: https://en.wikipedia.org/wiki/Cooperative_multitasking
- **urequests Library**: MicroPython HTTP client library

---

**Document Version:** 1.2  
**Last Updated:** February 11, 2026  
**Author:** Marco Alvarado Zamora

**Changelog:**
- **v1.2 (Feb 11, 2026)**: Added API synchronization support with ApiSyncTask for remote data transmission
- **v1.1 (Feb 10, 2026)**: Added internal flash storage support with DataLoggerTask and InternalStorageDriver
- **v1.0 (Jan 16, 2026)**: Initial documentation release

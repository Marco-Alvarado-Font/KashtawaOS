# KashtawaOS

KashtawaOS is the embedded firmware for an autonomous inventory control drone. This system integrates a Raspberry Pi Pico W to read RFID tags and collect inventory data, which is then transmitted to a centralized database for real-time inventory management.

> **Name Origin**: "Kashtawa" comes from Cabécar language, meaning "to count things" - perfectly describing the drone's inventory counting purpose.

## Features

- **RFID Tag Reading**: Automatic identification and tracking of inventory items
- **Ultrasonic Distance Sensing**: HC-SR04 sensor integration for obstacle detection and navigation
- **I2C LCD Display**: Real-time status and data visualization
- **Wireless Communication**: WiFi connectivity for data transmission to remote databases
- **Modular Architecture**: Easy-to-extend firmware structure for additional sensors and features

## Hardware Requirements

- Raspberry Pi Pico W
- HC-SR04 Ultrasonic Sensor
- I2C LCD Display (16x2 or 20x4)
- RFID Reader Module
- Power supply and mounting hardware

## Project Structure

## Getting Started

1. Flash the Raspberry Pi Pico W with the MicroPython firmware (RPI_PICO_W-20250911-v1.26.1.uf2)
2. Upload the firmware files to the device
3. Configure WiFi credentials in `wlan.py`
4. Connect the sensors according to the hardware specifications

## License


## Author

Marco Alvarado Zamora 

Developed for autonomous inventory management systems.

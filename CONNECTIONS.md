# CanSat Wiring & Connections Guide

This document describes all hardware connections between sensors, modules, and the Raspberry Pi Foundation Raspberry Pi Pico flight computer.

# Microcontroller Pin Reference

# Microcontroller: Raspberry Pi Pico

Function	GPIO Pin	Connected Component
I2C SDA	GP0	BMP280 SDA, MPU6050 SDA
I2C SCL	GP1	BMP280 SCL, MPU6050 SCL
UART TX	GP4	GPS RX
UART RX	GP5	GPS TX
SPI SCK	GP18	SD Card SCK
SPI MOSI	GP19	SD Card MOSI
SPI MISO	GP16	SD Card MISO
SPI CS	GP17	SD Card CS
3.3V	3V3	All sensors VCC
GND	GND	All sensors GND

# BMP280 Connection (Environmental Sensor)
BMP280 Pin	Connect to Pico

VCC ---	3.3V

GND ---	GND

SDA ---	GP0

SCL ---	GP1

Protocol: I2C
Address: 0x76

# MPU6050 Connection (IMU Sensor)
MPU6050 Pin	Connect to Pico
VCC ---	3.3V
GND ---	GND
SDA ---	GP0
SCL ---	GP1

Protocol: I2C
Address: 0x68

# GPS Module Connection
GPS Pin	Connect to Pico
VCC ---	3.3V
GND ---	GND
TX  ---	GP5
RX  ---	GP4

Protocol: UART
Baud rate: 9600

# MicroSD Card Module Connection
SD Card Pin	Connect to Pico
VCC  ---	3.3V
GND  ---	GND
SCK  ---	GP18
MOSI ---	GP19
MISO ---	GP16
CS	 ---  GP17

Protocol: SPI

# WiFi Telemetry

Provided by onboard MicroPython network stack.

Creates access point:

SSID: CANSAT_LIVE
Password: 12345678
Dashboard: http://192.168.4.1

# Power System
Component	Voltage
Pico -----	3.3V
Sensors	 -----3.3V
GPS -----	3.3V
SD Card -----	3.3V

# System Connection Diagram
        Raspberry Pi Pico
               │
    ┌──────────┼──────────┐
    │          │          │
 BMP280     MPU6050      GPS
 (I2C)       (I2C)      (UART)
    │          │          │
    └──────────┼──────────┘
               │
           MicroSD
            (SPI)

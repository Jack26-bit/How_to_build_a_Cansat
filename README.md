# How_to_build_a_Cansat
CanSat Live Telemetry System

An autonomous real-time atmospheric research platform built using the Raspberry Pi Pico. This CanSat collects environmental, motion, and GPS data during flight and transmits live telemetry to a wireless web dashboard while simultaneously logging mission data for post-flight analysis.


Overview

The CanSat Live Telemetry System is designed for high-altitude experiments, educational rocket launches, and atmospheric research. It operates autonomously, collecting and transmitting mission-critical data including temperature, pressure, altitude, orientation, and GPS location.

The system creates its own WiFi access point and hosts a live telemetry dashboard accessible from any smartphone or computer.

Key Features
Environmental Monitoring

BMP280 sensor for:

Temperature measurement

Atmospheric pressure measurement

Real-time altitude estimation

Motion Tracking

MPU6050 6-axis IMU provides:

3-axis accelerometer data

3-axis gyroscope data

Flight dynamics and orientation analysis

GPS Tracking

Real-time position tracking:

Latitude

Longitude

Altitude

Satellite count

Fault-Tolerant Data Logging

Automatic CSV logging to MicroSD card

Continues operating even if SD card fails

Ideal for post-flight analysis

Live Wireless Telemetry

Built-in WiFi Access Point

Real-time web dashboard at:

http://192.168.4.1


No internet required

Works with phones, tablets, and computers

Mission Timer

Tracks time since launch

Provides accurate mission timeline

System Architecture
                +------------------+
                | Raspberry Pi Pico|
                +--------+---------+
                         |
        +----------------+----------------+
        |                |                |
    BMP280           MPU6050            GPS
 (Temp/Pressure)   (Accel/Gyro)    (Location Data)
        |                |                |
        +----------------+----------------+
                         |
                   Data Processing
                         |
           +-------------+-------------+
           |                           |
       SD Card Logging          WiFi Telemetry
           |                           |
       CSV Data Storage         Live Web Dashboard

Technical Specifications
Component	Specification
Microcontroller	Raspberry Pi Pico
Environmental Sensor	BMP280
IMU	MPU6050
GPS Module	UART GPS Module
Data Storage	MicroSD Card
Communication	WiFi Access Point
Telemetry Interface	Web Dashboard
Logging Interval	1 second
Power	Battery powered

Software Features

The flight software (main.py) includes:

Sensor initialization and fault detection 

main

Real-time telemetry processing

SD card CSV logging

WiFi Access Point creation

Embedded web server with live dashboard

Fault-tolerant operation

Telemetry Dashboard

Features:

Live mission time

Temperature, pressure, altitude

Accelerometer and gyroscope data

GPS position and altitude

Satellite connection status

SD card logging status

Auto-refreshes every second.

Hardware Requirements

Required components:

Raspberry Pi Pico

BMP280 sensor

MPU6050 IMU

GPS module

MicroSD card module

Battery

Custom 3D printed CanSat structure (included)

How to Use
1. Flash MicroPython to Pico

Install MicroPython firmware on Raspberry Pi Pico.

2. Upload Imported files

Upload to Pico

3. Power On

The system will create:

WiFi Name:

CANSAT_LIVE


Password:

12345678

4. Connect to Dashboard

Open browser:

http://192.168.4.1

🛰️ Mission Capabilities

This CanSat is suitable for:

Rocket launches

High altitude balloon missions

Atmospheric research

STEM education

Aerospace experimentation

Telemetry system development

Example Logged Data
Time,Temp,Pressure,Altitude,AccelX,AccelY,AccelZ,GyroX,GyroY,GyroZ,Lat,Lon,GPSAlt,Sats
12.0,28.4,1009.2,34.5,0.01,-0.02,1.00,0.1,0.2,0.0,12.9716N,77.5946E,920,8

3D Printable Structure

Included STL files:

Main body tube

Nose cone

Electronics mount

Battery mount

Parachute system

Fully modular and printable.

Open Source Contribution

Contributions are welcome.

You can contribute by:

Improving flight software

Adding new sensors

Improving telemetry

Enhancing mechanical design

Adding new features

License

This project is licensed under the MIT License.

You are free to:

Use

Modify

Distribute

Build upon

Author

Neeraj Kiran Janakula  
Creator & Lead Developer — CanSat Live Telemetry System  
GitHub: https://github.com/Jack26-bit 
LinkedIn: https://www.linkedin.com/in/neeraj-kiran-janakula-904643384

Developed as an open-source CanSat telemetry platform for education and research.

Support the Project

If you found this useful:

Give it a ⭐ on GitHub.

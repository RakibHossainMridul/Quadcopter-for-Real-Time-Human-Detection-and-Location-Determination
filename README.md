# Quadcopter-for-Real-Time-Human-Detection-and-Location-Determination
This is our project for EEE 404: Robotics and Automation Laboratory.

![Drone_image](https://github.com/RakibHossainMridul/Quadcopter-for-Real-Time-Human-Detection-and-Location-Determination/blob/main/drone_project.jpg)
![Drone Top View](https://github.com/RakibHossainMridul/Quadcopter-for-Real-Time-Human-Detection-and-Location-Determination/blob/main/drone_top_view.jpg)


**Video Processing and Location Transmission System**

**Image Acquisition and Processing System**

The drone employs a dual-configuration imaging system that has undergone iterative improvements. Initially, a PiCamera was utilized, which was later upgraded to a Logitech C270p webcam capable of capturing 720p resolution footage. The image processing pipeline is implemented on a Raspberry Pi 4, which serves as the primary onboard computing unit.

Detection System Architecture
The system implements two distinct operational modes:
1. Onboard Processing: Direct human detection and bounding box generation on the Raspberry Pi
2. Server-based Processing: Raw data transmission to a server PC for processing
   Alternatively, the processing can be done on server PC.

Object Detection Implementation

After extensive testing between YOLOv7 and YOLOv3 architectures, YOLOv3 was selected as the primary detection model. The decision was based on:
- robust detection capability
- Lightweight nature, making it suitable for onboard processing
- Optimal balance between computational efficiency and detection accuracy

**Location Data Management and Communication**

Current Implementation
The system operates within a local network configuration:
- Raspberry Pi and Server PC connected via WiFi
- Communication established through IPv4 addressing
- Server receives IP address data
- Automatic geolocation tracking through API token integration

Proposed Enhancement
For expanded operational capability, the system design includes integration of SIM7600 A/SIM 7600X 4G LTE module:
- Direct GPS data acquisition
- Parallel communication architecture:
  - GPS module → Mission Planner
  - GPS module → Onboard microcontroller (ESP32) → Transmitter module

Control Systems

The drone implements a dual-control architecture:
1. Autonomous Operation:
   - Mission Planner integration for automated flight paths
   - Predefined mission execution capability

2. Manual Override:
   - Direct operator control
   - Real-time flight adjustment capability

System Integration and Data Flow

The complete system integrates multiple data streams:
1. Visual Data: Webcam → Raspberry Pi → Detection System
2. Location Data: GPS → Mission Planner/ESP32
3. Control Data: Manual Input/Mission Planner → Flight Controller

This integrated approach ensures robust operation while maintaining system flexibility for future enhancements and modifications.


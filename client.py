import io
import socket
import struct
import time
import cv2
import numpy as np
from picamera2 import Picamera2
import netifaces  # New import for getting network interfaces

def get_ip_addresses():
    """Get all IP addresses of the Raspberry Pi except localhost"""
    ip_addresses = []
    interfaces = netifaces.interfaces()
    
    for interface in interfaces:
        # Skip loopback interface
        if interface.startswith('lo'):
            continue
        
        addrs = netifaces.ifaddresses(interface)
        # Get IPv4 addresses
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip_addresses.append({
                    'interface': interface,
                    'ip': addr['addr']
                })
    
    return ip_addresses

# Change this to your laptop's IP address
SERVER_IP = '192.168.0.107'
SERVER_PORT = 8000

# Create and configure camera
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (720, 720)}))
picam2.start()

# Create socket and bind host
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
connection = client_socket.makefile('wb')

try:
    # Get IP addresses
    ip_addresses = get_ip_addresses()
    
    # Convert IP addresses to JSON string and then to bytes
    ip_data = str(ip_addresses).encode('utf-8')
    
    # Send length of IP data first
    connection.write(struct.pack('<L', len(ip_data)))
    connection.flush()
    
    # Send IP data
    connection.write(ip_data)
    connection.flush()
    
    start = time.time()
    stream = io.BytesIO()
    
    while True:
        # Capture frame
        frame = picam2.capture_array()
        # Convert to JPEG
        success, encoded_image = cv2.imencode('.jpg', frame)
        if success:
            # Convert to bytes
            image_data = encoded_image.tobytes()
            # Write size of the image
            connection.write(struct.pack('<L', len(image_data)))
            connection.flush()
            # Write image data
            connection.write(image_data)
            
            if time.time() - start > 3600:  # 60 minutes
                break
    
    connection.write(struct.pack('<L', 0))

finally:
    picam2.stop()
    connection.close()
    client_socket.close()

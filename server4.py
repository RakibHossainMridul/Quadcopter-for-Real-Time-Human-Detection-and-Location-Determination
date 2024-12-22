import socket
import struct
import cv2
import numpy as np
import os
import ast
import requests
import json
from typing import Dict, List

def get_geolocation(ip: str) -> Dict:
    """
    Get geolocation data for an IP address using ip-api.com (free tier)
    Returns a dictionary with location information
    """
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        return {}

def add_text_to_image(image: np.ndarray, text_lines: List[str], start_y: int = 30) -> np.ndarray:
    """
    Add multiple lines of text to an image
    Returns the modified image and the next y position
    """
    y_pos = start_y
    for text in text_lines:
        cv2.putText(image, text, (10, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        y_pos += 20
    return y_pos

# Check if model files exist
if not os.path.exists('yolov3.weights') or not os.path.exists('yolov3.cfg'):
    print("Error: YOLO files not found. Please download yolov3.weights and yolov3.cfg")
    exit()

# Load YOLO model
print("Loading YOLO model...")
net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')
print("Model loaded successfully!")

# Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

print("Waiting for connection...")
connection, client_address = server_socket.accept()
connection = connection.makefile('rb')
print(f"Connected to: {client_address}")

try:
    # First receive the IP address data length
    ip_data_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
    
    # Receive the IP address data
    ip_data = connection.read(ip_data_len).decode('utf-8')
    ip_addresses = ast.literal_eval(ip_data)
    
    # Get geolocation data for each IP
    for addr in ip_addresses:
        if addr['ip'] != '127.0.0.1':  # Skip localhost
            geo_data = get_geolocation(addr['ip'])
            addr['geo'] = geo_data
    
    print("\nRaspberry Pi Network Interfaces:")
    for addr in ip_addresses:
        print(f"Interface: {addr['interface']}, IP: {addr['ip']}")
        if 'geo' in addr:
            print(f"Location: {addr['geo'].get('city', 'N/A')}, {addr['geo'].get('country', 'N/A')}")
    print()
    
    while True:
        # Read the length of the image as a 32-bit unsigned int
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        
        # Construct a stream to hold the image data and read the image data
        image_stream = connection.read(image_len)
        image_array = np.frombuffer(image_stream, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Prepare image for YOLO
        height, width = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # Get detections
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        outputs = net.forward(output_layers)
        
        # Process detections
        boxes = []
        confidences = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5 and class_id == 0:  # class_id 0 is person
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
        
        # Add IP addresses and geolocation to the image
        text_lines = []
        for addr in ip_addresses:
            text_lines.append(f"{addr['interface']}: {addr['ip']}")
            if 'geo' in addr:
                geo = addr['geo']
                text_lines.append(f"Location: {geo.get('city', 'N/A')}, {geo.get('region', 'N/A')}, {geo.get('country', 'N/A')}")
                text_lines.append(f"Coords: {geo.get('lat', 'N/A')}, {geo.get('lon', 'N/A')}")
                text_lines.append(f"ISP: {geo.get('isp', 'N/A')}")
                text_lines.append("") # Empty line for spacing
        
        next_y = add_text_to_image(image, text_lines)
        
        # Apply non-maximum suppression
        if boxes:  # Only if we have detections
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            
            # Draw boxes
            for i in indices:
                i = i.item() if hasattr(i, 'item') else i
                box = boxes[i]
                x, y, w, h = box
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, f'Person {confidences[i]:.2f}', 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Show the frame
        cv2.imshow('Video Stream', image)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    connection.close()
    server_socket.close()
    cv2.destroyAllWindows()
import requests
import json
import time
import random

API_URL = "http://localhost:5000/predict"

# Sample data types for sensors
DATA_TYPES = ["Text", "Image", "Video", "Boolean", "Numerical"]
FILE_SIZES = ["Small", "Medium", "Large"]
SPEED_LEVELS = ["Low", "Medium", "High"]
SECURITY_LEVELS = ["Low", "Medium", "High"]
REAL_TIME_OPTIONS = ["Yes", "No"]
CONNECTIVITY_TYPES = ["WiFi", "Ethernet", "Cellular"]
COST_SENSITIVITY = ["Low", "Medium", "High"]

def simulate_sensor_request(sensor_id):
    """Simulate a sensor sending a request for encryption algorithm recommendation."""
    payload = {
        "sensor_id": sensor_id,
        "file_size": random.choice(FILE_SIZES),
        "data_type": random.choice(DATA_TYPES),
        "required_speed": random.choice(SPEED_LEVELS),
        "security_level": random.choice(SECURITY_LEVELS),
        "real_time": random.choice(REAL_TIME_OPTIONS),
        "connectivity": random.choice(CONNECTIVITY_TYPES),
        "cost_sensitivity": random.choice(COST_SENSITIVITY)
    }
    
    print(f"\nSensor {sensor_id} sending request with parameters:")
    for key, value in payload.items():
        if key != "sensor_id":
            print(f"  {key}: {value}")
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Sensor {sensor_id} received recommendation: {result['predicted_algorithm']}")
            return result
        else:
            print(f"Sensor {sensor_id} error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Sensor {sensor_id} connection error: {str(e)}")
        return None

def run_simulation(num_sensors=5, interval=2):
    """Run a simulation with multiple sensors."""
    print(f"Starting simulation with {num_sensors} sensors...")
    
    try:
        # First check if the API is available
        health_check = requests.get("http://localhost:5000/health")
        if health_check.status_code != 200:
            print("API is not available. Please start the Flask server first.")
            return
        
        print("API is running. Starting sensor simulation...")
        
        for i in range(10):  # Run 10 iterations
            print(f"\n--- Iteration {i+1} ---")
            for sensor_id in range(1, num_sensors + 1):
                simulate_sensor_request(sensor_id)
                time.sleep(interval / num_sensors)  # Stagger the requests
            
            time.sleep(interval)
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API. Is the Flask server running?")
    
    print("\nSimulation completed.")

def send_specific_request():
    """Send a specific request with user-defined parameters."""
    print("Send a specific request to the encryption algorithm API")
    print("Please provide the following parameters:")
    
    payload = {
        "file_size": input(f"File Size {FILE_SIZES}: "),
        "data_type": input(f"Data Type {DATA_TYPES}: "),
        "required_speed": input(f"Required Speed {SPEED_LEVELS}: "),
        "security_level": input(f"Security Level {SECURITY_LEVELS}: "),
        "real_time": input(f"Real-Time Requirement {REAL_TIME_OPTIONS}: "),
        "connectivity": input(f"Connectivity Type {CONNECTIVITY_TYPES}: "),
        "cost_sensitivity": input(f"Cost Sensitivity {COST_SENSITIVITY}: ")
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\nResult:")
            print(f"Recommended encryption algorithm: {result['predicted_algorithm']}")
            print("\nInput parameters:")
            for key, value in result['input_parameters'].items():
                print(f"  {key}: {value}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API. Is the Flask server running?")

if __name__ == "__main__":
    print("Encryption Algorithm Recommendation - Sensor Client")
    print("---------------------------------------------------")
    print("1. Run simulation with multiple sensors")
    print("2. Send a specific request")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == "1":
        num_sensors = int(input("Number of sensors to simulate: "))
        interval = float(input("Interval between iterations (seconds): "))
        run_simulation(num_sensors, interval)
    elif choice == "2":
        send_specific_request()
    else:
        print("Exiting.")
"""
Manages automatic subscriptions to Orion Context Broker.
Creates subscriptions for temperature/humidity and GPS sensors.
"""
import requests
import time
import json
import os
import configuration as config

# Orion Context Broker URL
ORION_URL = os.getenv('ORION_URL', 'http://orion:1026')

def create_temp_humidity_subscription():
    """Creates subscription for temperature and humidity sensor data."""
    subscription_data = {
        "description": "Notificar sensor de temperatura y humedad",
        "subject": {
            "entities": [{
                "idPattern": ".*",
                "type": "sensorTempHum"
            }],
            "condition": {
                "attrs": [
                    "temperatura",
                    "humedad"
                ]
            }
        },
        "notification": {
            "attrs": [
                "id",
                "temperatura",
                "humedad"
            ],
            "http": {
                "url": "http://quantumleap:8668/v2/notify"
            },
            "metadata": [
                "dateCreated",
                "dateModified"
            ]
        }
    }
    
    return create_subscription(subscription_data, "Temperature/Humidity")

def create_gps_subscription():
    """Creates subscription for GPS sensor data."""
    subscription_data = {
        "description": "Notificar sensor de GPS",
        "subject": {
            "entities": [{
                "idPattern": ".*",
                "type": "sensorGPS"
            }],
            "condition": {
                "attrs": [
                    "latitud",
                    "longitud"
                ]
            }
        },
        "notification": {
            "attrs": [
                "id",
                "latitud",
                "longitud"
            ],
            "http": {
                "url": "http://quantumleap:8668/v2/notify"
            },
            "metadata": [
                "dateCreated",
                "dateModified"
            ]
        }
    }
    
    return create_subscription(subscription_data, "GPS")

def create_subscription(subscription_data, subscription_type):
    """Creates a subscription in Orion Context Broker."""
    url = f"{ORION_URL}/v2/subscriptions"
    headers = {
        'Content-Type': 'application/json',
        'Fiware-Service': 'smart',
        'Fiware-ServicePath': '/'
    }
    
    try:
        print(f"Creating {subscription_type} subscription...")
        response = requests.post(url, json=subscription_data, headers=headers, timeout=30)
        
        if response.status_code == 201:
            subscription_id = response.headers.get('Location', '').split('/')[-1]
            print(f"✓ {subscription_type} subscription created successfully! ID: {subscription_id}")
            return True
        elif response.status_code == 422:
            # Subscription might already exist, check if it's our subscription
            print(f"⚠ {subscription_type} subscription might already exist (422 error)")
            return check_existing_subscription(subscription_data, subscription_type)
        else:
            print(f"✗ Failed to create {subscription_type} subscription. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating {subscription_type} subscription: {e}")
        return False

def check_existing_subscription(subscription_data, subscription_type):
    """Check if a similar subscription already exists."""
    url = f"{ORION_URL}/v2/subscriptions"
    headers = {
        'Accept': 'application/json',
        'Fiware-Service': 'smart',
        'Fiware-ServicePath': '/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            subscriptions = response.json()
            for sub in subscriptions:
                if sub.get('description') == subscription_data.get('description'):
                    print(f"✓ {subscription_type} subscription already exists with ID: {sub.get('id')}")
                    return True
            print(f"⚠ No existing {subscription_type} subscription found, but creation failed")
            return False
        else:
            print(f"✗ Failed to check existing {subscription_type} subscriptions")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error checking existing {subscription_type} subscriptions: {e}")
        return False

def wait_for_orion():
    """Wait for Orion Context Broker to be available."""
    print("Waiting for Orion Context Broker...")
    for i in range(1, config.MAX_RETRIES + 1):
        try:
            response = requests.get(f"{ORION_URL}/version", timeout=10)
            if response.status_code == 200:
                print("✓ Orion Context Broker is available!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if i < config.MAX_RETRIES:
            print(f"Orion not ready, retrying in {config.RETRY_DELAY} seconds... (attempt {i}/{config.MAX_RETRIES})")
            time.sleep(config.RETRY_DELAY)
    
    print("✗ Failed to connect to Orion Context Broker")
    return False

def setup_subscriptions():
    """Setup all automatic subscriptions."""
    print("=" * 50)
    print("Setting up automatic subscriptions...")
    print("=" * 50)
    
    # Wait for Orion to be available
    if not wait_for_orion():
        print("✗ Cannot setup subscriptions - Orion Context Broker not available")
        return False
    
    # Create subscriptions
    results = []
    results.append(create_temp_humidity_subscription())
    results.append(create_gps_subscription())
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 50)
    print(f"Subscription setup completed: {success_count}/{total_count} successful")
    print("=" * 50)
    
    return success_count == total_count

if __name__ == "__main__":
    setup_subscriptions()
"""
Manages automatic entity initialization in Orion Context Broker.
Creates initial sensor entities for temperature/humidity and GPS sensors.
"""
import requests
import time
import json
import os
import configuration as config

# Orion Context Broker URL
ORION_URL = os.getenv('ORION_URL', 'http://orion:1026')

def create_temp_humidity_entity():
    """Creates initial temperature and humidity sensor entity."""
    entity_data = {
        "id": "sensor001",
        "type": "sensorTempHum",
        "temperatura": {
            "value": 25.1,
            "type": "float"
        },
        "humedad": {
            "value": 58.5,
            "type": "float"
        }
    }
    
    return create_entity(entity_data, "Temperature/Humidity Sensor")

def create_gps_entity():
    """Creates initial GPS sensor entity."""
    entity_data = {
        "id": "sensor002",
        "type": "sensorGPS",
        "latitude": {
            "value": 6.26195,
            "type": "float"
        },
        "longitude": {
            "value": -75.59046,
            "type": "float"
        }
    }
    
    return create_entity(entity_data, "GPS Sensor")

def create_entity(entity_data, entity_type):
    """Creates an entity in Orion Context Broker."""
    url = f"{ORION_URL}/v2/entities"
    headers = {
        'Content-Type': 'application/json',
        'Fiware-Service': 'smart',
        'Fiware-ServicePath': '/'
    }
    
    try:
        print(f"Creating {entity_type} entity...")
        response = requests.post(url, json=entity_data, headers=headers, timeout=30)
        
        if response.status_code == 201:
            print(f"✓ {entity_type} entity created successfully! ID: {entity_data['id']}")
            return True
        elif response.status_code == 422:
            # Entity might already exist, check and update if necessary
            print(f"⚠ {entity_type} entity might already exist (422 error)")
            return update_existing_entity(entity_data, entity_type)
        else:
            print(f"✗ Failed to create {entity_type} entity. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating {entity_type} entity: {e}")
        return False

def update_existing_entity(entity_data, entity_type):
    """Updates an existing entity or creates it if it doesn't exist."""
    entity_id = entity_data['id']
    url = f"{ORION_URL}/v2/entities/{entity_id}"
    headers = {
        'Content-Type': 'application/json',
        'Fiware-Service': 'smart',
        'Fiware-ServicePath': '/'
    }
    
    try:
        # First, check if entity exists
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print(f"✓ {entity_type} entity already exists with ID: {entity_id}")
            
            # Update entity attributes
            update_data = {key: value for key, value in entity_data.items() 
                          if key not in ['id', 'type']}
            
            update_response = requests.patch(
                f"{url}/attrs", 
                json=update_data, 
                headers=headers, 
                timeout=30
            )
            
            if update_response.status_code in [200, 204]:
                print(f"✓ {entity_type} entity updated successfully!")
                return True
            else:
                print(f"⚠ Failed to update {entity_type} entity")
                return True  # Entity exists, even if update failed
                
        elif response.status_code == 404:
            # Entity doesn't exist, try to create again
            print(f"Entity {entity_id} not found, attempting to create...")
            return create_entity(entity_data, entity_type)
        else:
            print(f"✗ Error checking {entity_type} entity existence")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error updating {entity_type} entity: {e}")
        return False

def list_entities():
    """List all entities in Orion Context Broker."""
    url = f"{ORION_URL}/v2/entities"
    headers = {
        'Accept': 'application/json',
        'Fiware-Service': 'smart',
        'Fiware-ServicePath': '/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            entities = response.json()
            print(f"Found {len(entities)} entities in Orion Context Broker:")
            for entity in entities:
                print(f"  - ID: {entity.get('id')}, Type: {entity.get('type')}")
            return entities
        else:
            print(f"✗ Failed to list entities. Status: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"✗ Error listing entities: {e}")
        return []

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

def setup_entities():
    """Setup all initial sensor entities."""
    print("=" * 50)
    print("Setting up initial sensor entities...")
    print("=" * 50)
    
    # Wait for Orion to be available
    if not wait_for_orion():
        print("✗ Cannot setup entities - Orion Context Broker not available")
        return False
    
    # Create entities
    results = []
    results.append(create_temp_humidity_entity())
    results.append(create_gps_entity())
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 50)
    print(f"Entity setup completed: {success_count}/{total_count} successful")
    
    # List all entities for verification
    print("\nCurrent entities in Orion Context Broker:")
    list_entities()
    
    print("=" * 50)
    
    return success_count == total_count

def get_entity_by_id(entity_id):
    """Get specific entity by ID."""
    url = f"{ORION_URL}/v2/entities/{entity_id}"
    headers = {
        'Accept': 'application/json',
        'Fiware-Service': 'smart',
        'Fiware-ServicePath': '/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Error getting entity {entity_id}: {e}")
        return None

if __name__ == "__main__":
    setup_entities()
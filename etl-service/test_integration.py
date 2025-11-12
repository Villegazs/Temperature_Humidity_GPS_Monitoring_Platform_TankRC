"""
Test script to verify entity and subscription setup.
Run this script to test the Orion Context Broker integration.
"""
import requests
import json
import time

# Configuration
ETL_SERVICE_URL = "http://localhost:8080"
ORION_URL = "http://localhost:1026"

def test_etl_service_health():
    """Test ETL service is running."""
    try:
        response = requests.get(f"{ETL_SERVICE_URL}/etl")
        if response.status_code == 200:
            print("✓ ETL Service is running")
            return True
        else:
            print(f"✗ ETL Service health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ ETL Service connection failed: {e}")
        return False

def test_subscription_health():
    """Test subscription system health."""
    try:
        response = requests.get(f"{ETL_SERVICE_URL}/subscriptions/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Subscription Health: {data['status']}")
            print(f"  - Orion reachable: {data['orion_reachable']}")
            print(f"  - Active subscriptions: {data['active_subscriptions']}/{data['expected_subscriptions']}")
            print(f"  - Active entities: {data['active_entities']}/{data['expected_entities']}")
            return data['status'] == 'healthy'
        else:
            print(f"✗ Subscription health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Subscription health check failed: {e}")
        return False

def test_list_entities():
    """Test listing entities."""
    try:
        response = requests.get(f"{ETL_SERVICE_URL}/subscriptions/entities")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Listed {data['total_entities']} entities")
            for entity in data['entities']:
                print(f"  - {entity['id']} ({entity['type']})")
            return True
        else:
            print(f"✗ Failed to list entities: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to list entities: {e}")
        return False

def test_get_specific_entity(entity_id):
    """Test getting a specific entity."""
    try:
        response = requests.get(f"{ETL_SERVICE_URL}/subscriptions/entities/{entity_id}")
        if response.status_code == 200:
            data = response.json()
            entity = data['entity']
            print(f"✓ Retrieved entity {entity_id}:")
            print(f"  - Type: {entity['type']}")
            for attr, value in entity.items():
                if attr not in ['id', 'type']:
                    print(f"  - {attr}: {value['value']} ({value['type']})")
            return True
        else:
            print(f"✗ Failed to get entity {entity_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to get entity {entity_id}: {e}")
        return False

def test_orion_direct():
    """Test direct connection to Orion."""
    try:
        headers = {
            'Accept': 'application/json',
            'Fiware-Service': 'smart',
            'Fiware-ServicePath': '/'
        }
        
        # Test Orion version
        response = requests.get(f"{ORION_URL}/version")
        if response.status_code == 200:
            print("✓ Orion Context Broker is accessible")
        else:
            print(f"✗ Orion version check failed: {response.status_code}")
            return False
        
        # Test entities
        response = requests.get(f"{ORION_URL}/v2/entities", headers=headers)
        if response.status_code == 200:
            entities = response.json()
            print(f"✓ Direct Orion query: {len(entities)} entities")
            return True
        else:
            print(f"✗ Direct Orion entity query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Direct Orion test failed: {e}")
        return False

def setup_entities_if_needed():
    """Setup entities if they don't exist."""
    try:
        response = requests.post(f"{ETL_SERVICE_URL}/subscriptions/entities/setup")
        if response.status_code == 200:
            print("✓ Entities setup successful")
            return True
        else:
            print(f"⚠ Entity setup response: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Entity setup failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing Orion Context Broker Integration")
    print("=" * 60)
    
    # Test ETL Service
    print("\n1. Testing ETL Service...")
    if not test_etl_service_health():
        print("❌ ETL Service not available. Please start the service first.")
        return
    
    # Test Subscription Health
    print("\n2. Testing Subscription System...")
    test_subscription_health()
    
    # Test Direct Orion Connection
    print("\n3. Testing Direct Orion Connection...")
    test_orion_direct()
    
    # List Entities
    print("\n4. Listing Entities...")
    test_list_entities()
    
    # Test specific entities
    print("\n5. Testing Specific Entities...")
    test_get_specific_entity("sensor001")  # Temperature/Humidity
    test_get_specific_entity("sensor002")  # GPS
    
    # Setup entities if needed
    print("\n6. Setting up entities if needed...")
    setup_entities_if_needed()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
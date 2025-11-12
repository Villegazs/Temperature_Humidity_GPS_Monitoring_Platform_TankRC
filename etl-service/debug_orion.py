"""
Debug script to test Orion Context Broker subscriptions and entities.
Use this to troubleshoot subscription visibility issues.
"""
import requests
import json
import configuration as config

# Orion Context Broker URL - usar IP pública para pruebas externas
# En producción, usar config.ORION_URL para conexiones internas del contenedor
ORION_URL = config.ORION_URL

# Standard FIWARE headers
FIWARE_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Fiware-Service': 'smart',
    'Fiware-ServicePath': '/'
}

def test_orion_connection():
    """Test basic connection to Orion."""
    print("🔍 Testing Orion Connection...")
    try:
        response = requests.get(f"{ORION_URL}/version", timeout=10)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✓ Orion Context Broker is accessible")
            print(f"  - Version: {version_info.get('orion', {}).get('version', 'Unknown')}")
            print(f"  - URL: {ORION_URL}")
            return True
        else:
            print(f"✗ Orion connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Orion connection error: {e}")
        return False

def list_subscriptions_with_service():
    """List subscriptions with FIWARE service headers."""
    print("\n🔍 Listing subscriptions with FIWARE headers...")
    try:
        response = requests.get(f"{ORION_URL}/v2/subscriptions", headers=FIWARE_HEADERS, timeout=30)
        print(f"Request URL: {ORION_URL}/v2/subscriptions")
        print(f"Request Headers: {FIWARE_HEADERS}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            subscriptions = response.json()
            print(f"✓ Found {len(subscriptions)} subscriptions with FIWARE headers")
            for i, sub in enumerate(subscriptions, 1):
                print(f"  {i}. ID: {sub.get('id', 'N/A')}")
                print(f"     Description: {sub.get('description', 'N/A')}")
                print(f"     Status: {sub.get('status', 'N/A')}")
            return subscriptions
        else:
            print(f"✗ Failed to list subscriptions: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error listing subscriptions: {e}")
        return []

def list_subscriptions_without_service():
    """List subscriptions without FIWARE service headers."""
    print("\n🔍 Listing subscriptions without FIWARE headers...")
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{ORION_URL}/v2/subscriptions", headers=headers, timeout=30)
        print(f"Request URL: {ORION_URL}/v2/subscriptions")
        print(f"Request Headers: {headers}")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            subscriptions = response.json()
            print(f"✓ Found {len(subscriptions)} subscriptions without FIWARE headers")
            for i, sub in enumerate(subscriptions, 1):
                print(f"  {i}. ID: {sub.get('id', 'N/A')}")
                print(f"     Description: {sub.get('description', 'N/A')}")
                print(f"     Status: {sub.get('status', 'N/A')}")
            return subscriptions
        else:
            print(f"✗ Failed to list subscriptions: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error listing subscriptions: {e}")
        return []

def list_entities_with_service():
    """List entities with FIWARE service headers."""
    print("\n🔍 Listing entities with FIWARE headers...")
    try:
        response = requests.get(f"{ORION_URL}/v2/entities", headers=FIWARE_HEADERS, timeout=30)
        print(f"Request URL: {ORION_URL}/v2/entities")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            entities = response.json()
            print(f"✓ Found {len(entities)} entities with FIWARE headers")
            for i, entity in enumerate(entities, 1):
                print(f"  {i}. ID: {entity.get('id', 'N/A')}")
                print(f"     Type: {entity.get('type', 'N/A')}")
            return entities
        else:
            print(f"✗ Failed to list entities: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error listing entities: {e}")
        return []

def test_create_simple_subscription():
    """Create a simple test subscription."""
    print("\n🔍 Creating simple test subscription...")
    
    test_subscription = {
        "description": "TEST - Simple subscription for debugging",
        "subject": {
            "entities": [
                {
                    "id": "sensor001",
                    "type": "sensorTempHum"
                }
            ],
            "condition": {
                "attrs": ["temperatura"]
            }
        },
        "notification": {
            "http": {
                "url": "http://quantumleap:8668/v2/notify"
            },
            "attrs": ["temperatura"]
        }
    }
    
    try:
        print(f"Request URL: {ORION_URL}/v2/subscriptions")
        print(f"Request Headers: {FIWARE_HEADERS}")
        print(f"Request Body: {json.dumps(test_subscription, indent=2)}")
        
        response = requests.post(
            f"{ORION_URL}/v2/subscriptions", 
            json=test_subscription, 
            headers=FIWARE_HEADERS, 
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            subscription_id = response.headers.get('Location', '').split('/')[-1]
            print(f"✓ Test subscription created successfully! ID: {subscription_id}")
            return subscription_id
        else:
            print(f"✗ Test subscription creation failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating test subscription: {e}")
        return None

def delete_subscription(subscription_id):
    """Delete a subscription by ID."""
    if not subscription_id:
        return False
        
    print(f"\n🔍 Deleting subscription {subscription_id}...")
    try:
        response = requests.delete(
            f"{ORION_URL}/v2/subscriptions/{subscription_id}",
            headers=FIWARE_HEADERS,
            timeout=30
        )
        
        if response.status_code == 204:
            print(f"✓ Subscription {subscription_id} deleted successfully")
            return True
        else:
            print(f"✗ Failed to delete subscription: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error deleting subscription: {e}")
        return False

def main():
    """Run comprehensive Orion debugging."""
    print("=" * 60)
    print("🔧 Orion Context Broker Debug Script")
    print("=" * 60)
    
    # Test basic connection
    if not test_orion_connection():
        print("❌ Cannot proceed - Orion not accessible")
        return
    
    # List subscriptions with different header configurations
    subs_with_service = list_subscriptions_with_service()
    subs_without_service = list_subscriptions_without_service()
    
    # List entities
    entities = list_entities_with_service()
    
    # Test creating a subscription
    test_sub_id = test_create_simple_subscription()
    
    # List subscriptions again to see if our test subscription appears
    print("\n" + "=" * 40)
    print("📋 After creating test subscription:")
    print("=" * 40)
    list_subscriptions_with_service()
    list_subscriptions_without_service()
    
    # Clean up test subscription
    if test_sub_id:
        delete_subscription(test_sub_id)
    
    print("\n" + "=" * 60)
    print("🏁 Debug completed!")
    print("=" * 60)
    
    # Summary
    print(f"📊 Summary:")
    print(f"  - Subscriptions with FIWARE headers: {len(subs_with_service)}")
    print(f"  - Subscriptions without FIWARE headers: {len(subs_without_service)}")
    print(f"  - Entities found: {len(entities)}")

if __name__ == "__main__":
    main()
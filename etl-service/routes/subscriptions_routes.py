"""
Routes for subscription management and monitoring.
"""
from flask import Blueprint, jsonify, request
import requests
import configuration as config

# Create Blueprint
subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

@subscriptions_bp.route('/', methods=['GET'])
def list_subscriptions():
    """List all active subscriptions in Orion Context Broker."""
    try:
        orion_url = config.ORION_URL
        headers = {
            'Accept': 'application/json',
            'Fiware-Service': 'smart',
            'Fiware-ServicePath': '/'
        }
        
        response = requests.get(f"{orion_url}/v2/subscriptions", headers=headers, timeout=30)
        
        if response.status_code == 200:
            subscriptions = response.json()
            return jsonify({
                "status": "success",
                "total_subscriptions": len(subscriptions),
                "subscriptions": subscriptions
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to retrieve subscriptions. Status: {response.status_code}",
                "response": response.text
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Error connecting to Orion Context Broker: {str(e)}"
        }), 500

@subscriptions_bp.route('/recreate', methods=['POST'])
def recreate_subscriptions():
    """Recreate automatic subscriptions."""
    try:
        from subscriptions import setup_subscriptions
        
        success = setup_subscriptions()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "All subscriptions recreated successfully"
            })
        else:
            return jsonify({
                "status": "partial_success",
                "message": "Some subscriptions failed to be created. Check logs for details."
            }), 207
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error recreating subscriptions: {str(e)}"
        }), 500

@subscriptions_bp.route('/health', methods=['GET'])
def subscription_health():
    """Check health of subscription system."""
    try:
        orion_url = config.ORION_URL
        
        # Check if Orion is reachable
        response = requests.get(f"{orion_url}/version", timeout=10)
        orion_status = response.status_code == 200
        
        # Get subscription count
        if orion_status:
            headers = {
                'Accept': 'application/json',
                'Fiware-Service': 'smart',
                'Fiware-ServicePath': '/'
            }
            subs_response = requests.get(f"{orion_url}/v2/subscriptions", headers=headers, timeout=30)
            subscription_count = len(subs_response.json()) if subs_response.status_code == 200 else 0
            
            # Get entity count
            entities_response = requests.get(f"{orion_url}/v2/entities", headers=headers, timeout=30)
            entity_count = len(entities_response.json()) if entities_response.status_code == 200 else 0
        else:
            subscription_count = 0
            entity_count = 0
        
        return jsonify({
            "status": "healthy" if orion_status else "unhealthy",
            "orion_reachable": orion_status,
            "orion_url": orion_url,
            "active_subscriptions": subscription_count,
            "expected_subscriptions": 2,  # Temperature/Humidity + GPS
            "active_entities": entity_count,
            "expected_entities": 2  # sensor001 (TempHum) + sensor002 (GPS)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }), 500

@subscriptions_bp.route('/entities', methods=['GET'])
def list_entities():
    """List all entities in Orion Context Broker."""
    try:
        from entities import list_entities
        
        entities = list_entities()
        return jsonify({
            "status": "success",
            "total_entities": len(entities),
            "entities": entities
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error listing entities: {str(e)}"
        }), 500

@subscriptions_bp.route('/entities/setup', methods=['POST'])
def setup_entities():
    """Setup initial sensor entities."""
    try:
        from entities import setup_entities
        
        success = setup_entities()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "All sensor entities created successfully"
            })
        else:
            return jsonify({
                "status": "partial_success",
                "message": "Some entities failed to be created. Check logs for details."
            }), 207
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error setting up entities: {str(e)}"
        }), 500

@subscriptions_bp.route('/entities/<entity_id>', methods=['GET'])
def get_entity(entity_id):
    """Get specific entity by ID."""
    try:
        from entities import get_entity_by_id
        
        entity = get_entity_by_id(entity_id)
        
        if entity:
            return jsonify({
                "status": "success",
                "entity": entity
            })
        else:
            return jsonify({
                "status": "not_found",
                "message": f"Entity {entity_id} not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error retrieving entity: {str(e)}"
        }), 500
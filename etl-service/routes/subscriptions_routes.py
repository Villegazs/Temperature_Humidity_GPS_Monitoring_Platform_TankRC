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
        else:
            subscription_count = 0
        
        return jsonify({
            "status": "healthy" if orion_status else "unhealthy",
            "orion_reachable": orion_status,
            "orion_url": orion_url,
            "active_subscriptions": subscription_count,
            "expected_subscriptions": 2  # Temperature/Humidity + GPS
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }), 500
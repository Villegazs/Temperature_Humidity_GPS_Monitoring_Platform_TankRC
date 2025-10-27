"""
Main entry point for the Unified ETL Service application.
- Initializes the Flask app
- Registers the blueprints for different services
- Starts the background schedulers
- Runs the web server
"""
from flask import Flask, jsonify
from utils import wait_for_crate, wait_for_mongo
from scheduler import start_schedulers
from services.irrigation_service import etl_process_irrigation
from services.gps_service import etl_process_gps

# Import Blueprints
from routes.irrigation_routes import irrigation_bp
from routes.gps_routes import gps_bp

# Initialize Flask App
app = Flask(__name__)

# Register Blueprints
app.register_blueprint(irrigation_bp)
app.register_blueprint(gps_bp)

@app.route('/')
def home():
    return jsonify({
        "message": "Unified ETL Service is running.",
        "services": {
            "irrigation": {
                "latest_kpi": "/irrigation",
                "history": "/irrigation/historial",
                "run_manual_etl": "POST to /irrigation/run-etl"
            },
            "gps": {
                "latest_location": "/gps",
                "history": "/gps/historial",
                "run_manual_etl": "POST to /gps/run-etl"
            }
        }
    })

if __name__ == '__main__':
    print("="*60)
    print("🚀 Starting Unified ETL System (Modular Architecture)")
    print("="*60)
    
    # Wait for databases to be ready
    wait_for_crate()
    wait_for_mongo()
    
    # Start background schedulers
    start_schedulers()
    
    print("\n✓ REST API started on port 8080.")
    print("="*60)
    
    # Run initial ETLs
    print("\n🔄 Running initial Irrigation ETL...")
    etl_process_irrigation()
    print("\n🔄 Running initial GPS ETL...")
    etl_process_gps()
    
    # Start Flask server
    app.run(debug=True, host='0.0.0.0', port=8080)
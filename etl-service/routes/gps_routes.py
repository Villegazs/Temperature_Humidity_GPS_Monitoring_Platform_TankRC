"""
Defines all API endpoints related to the GPS service.
Uses a Flask Blueprint to keep routes organized.
"""
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from services.gps_service import etl_process_gps
import configuration as config

gps_bp = Blueprint('gps_bp', __name__)

@gps_bp.route('/gps', methods=['GET'])
def get_latest_gps_location():
    try:
        client_mongo = MongoClient(config.MONGO_DB_URL)
        db = client_mongo[config.MONGO_GPS_DB]
        latest_record = db[config.MONGO_GPS_COLLECTION].find_one(sort=[("timestamp", -1)])
        client_mongo.close()
        if latest_record:
            latest_record['_id'] = str(latest_record['_id'])
            latest_record['timestamp'] = str(latest_record['timestamp'])
            if 'sensor_time_index' in latest_record:
                latest_record['sensor_time_index'] = str(latest_record['sensor_time_index'])
            return jsonify(latest_record)
        return jsonify({"message": "No location data available yet."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gps_bp.route('/gps/run-etl', methods=['POST'])
def run_gps_etl_manual():
    etl_process_gps()
    return jsonify({"message": "GPS ETL process executed successfully"}), 200

@gps_bp.route('/gps/historial', methods=['GET'])
def get_gps_history():
    try:
        limit = request.args.get('limit', 10, type=int)
        client_mongo = MongoClient(config.MONGO_DB_URL)
        db = client_mongo[config.MONGO_GPS_DB]
        records = list(db[config.MONGO_GPS_COLLECTION].find().sort("timestamp", -1).limit(limit))
        client_mongo.close()
        for record in records:
            record['_id'] = str(record['_id'])
            record['timestamp'] = str(record['timestamp'])
            if 'sensor_time_index' in record:
                record['sensor_time_index'] = str(record['sensor_time_index'])
        return jsonify({"total": len(records), "records": records}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
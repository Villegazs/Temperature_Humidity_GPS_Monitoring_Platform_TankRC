"""
Defines all API endpoints related to the irrigation service.
Uses a Flask Blueprint to keep routes organized.
"""
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from services.irrigation_service import etl_process_irrigation
import configuration as config

irrigation_bp = Blueprint('irrigation_bp', __name__)

@irrigation_bp.route('/irrigation', methods=['GET'])
def get_latest_irrigation_kpi():
    try:
        client_mongo = MongoClient(config.MONGO_DB_URL)
        db = client_mongo[config.MONGO_IRRIGATION_DB]
        latest_record = db[config.MONGO_IRRIGATION_COLLECTION].find_one(sort=[("timestamp", -1)])
        client_mongo.close()
        if latest_record:
            latest_record['_id'] = str(latest_record['_id'])
            latest_record['timestamp'] = str(latest_record['timestamp'])
            if 'sensor_time_index' in latest_record:
                latest_record['sensor_time_index'] = str(latest_record['sensor_time_index'])
            return jsonify(latest_record)
        return jsonify({"message": "No KPI data available yet."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@irrigation_bp.route('/irrigation/run-etl', methods=['POST'])
def run_irrigation_etl_manual():
    etl_process_irrigation()
    return jsonify({"message": "Irrigation ETL process executed successfully"}), 200

@irrigation_bp.route('/irrigation/historial', methods=['GET'])
def get_irrigation_history():
    try:
        limit = request.args.get('limit', 10, type=int)
        client_mongo = MongoClient(config.MONGO_DB_URL)
        db = client_mongo[config.MONGO_IRRIGATION_DB]
        records = list(db[config.MONGO_IRRIGATION_COLLECTION].find().sort("timestamp", -1).limit(limit))
        client_mongo.close()
        for record in records:
            record['_id'] = str(record['_id'])
            record['timestamp'] = str(record['timestamp'])
            if 'sensor_time_index' in record:
                record['sensor_time_index'] = str(record['sensor_time_index'])
        return jsonify({"total": len(records), "records": records}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
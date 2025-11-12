"""
Contains all the business logic for the GPS ETL process.
- Extracts data from CrateDB
- Loads data into MongoDB
"""
from datetime import datetime
from pymongo import MongoClient
from crate import client
import configuration as config

def get_last_gps_data():
    """Extracts the latest GPS coordinates from CrateDB."""
    try:
        with client.connect(config.CRATE_DB_URL) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT time_index, latitud, longitud FROM etsensorgps "
                "WHERE entity_id='sensor002' "
                "ORDER BY time_index DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                return {"time_index": row[0], "latitude": row[1], "longitude": row[2]}
            return None
    except Exception as e:
        print(f"❌ Error getting GPS data from CrateDB: {e}")
        return None

def save_location_to_mongo(sensor_time, latitude, longitude):
    """Loads the GPS location into MongoDB."""
    try:
        client_mongo = MongoClient(config.MONGO_DB_URL)
        db = client_mongo[config.MONGO_GPS_DB]
        collection = db[config.MONGO_GPS_COLLECTION]
        document = {
            "timestamp": datetime.now(),
            "sensor_time_index": sensor_time,
            "location": {"type": "Point", "coordinates": [longitude, latitude]},
            "processed": True
        }
        result = collection.insert_one(document)
        client_mongo.close()
        print(f"GPS Location saved to MongoDB with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error saving location to MongoDB: {e}")
        return None

def etl_process_gps():
    """Runs the complete ETL process for GPS data."""
    print(f"\n[{datetime.now()}] --- Starting GPS ETL Process ---")
    gps_data = get_last_gps_data()
    if not gps_data:
        print("GPS ETL Stop: Could not get GPS data.")
        return
    print(f"  EXTRACT (GPS): Latest location is Lat: {gps_data['latitude']}, Lon: {gps_data['longitude']}")
    print("  TRANSFORM (GPS): No transformation required.")
    save_id = save_location_to_mongo(gps_data['time_index'], gps_data['latitude'], gps_data['longitude'])
    if save_id:
        print("  LOAD (GPS): Successfully loaded data to MongoDB.")
    else:
        print("ETL Error (GPS): Failed to load data to MongoDB.")
    print("--- GPS ETL Process Finished ---")
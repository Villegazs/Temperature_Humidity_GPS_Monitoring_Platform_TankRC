"""
Contains all the business logic for the Irrigation ETL process.
- Extracts data from CrateDB
- Transforms data by calculating KPI
- Loads data into MongoDB
"""
from datetime import datetime
from pymongo import MongoClient
from crate import client
import configuration as config

def get_last_irrigation_data():
    """Extracts the latest temperature and humidity reading from CrateDB."""
    try:
        with client.connect(config.CRATE_DB_URL) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT time_index, temperatura, humedad FROM etsensortemphum "
                "WHERE entity_id='sensor001' "
                "ORDER BY time_index DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                return {"time_index": row[0], "temperature": row[1], "humidity": row[2]}
            return None
    except Exception as e:
        print(f"❌ Error getting irrigation data from CrateDB: {e}")
        return None

def calculate_kpi(temperature, humidity):
    """Calculates the irrigation KPI based on temperature and humidity."""
    if temperature < 15:
        base_kpi = {"action": "no_irrigation", "level": 0, "description": f"Temperatura baja ({temperature}°C)"}
    elif 15 <= temperature < 20:
        base_kpi = {"action": "minimum_irrigation", "level": 1, "description": f"Temperatura moderada-baja ({temperature}°C)"}
    elif 20 <= temperature < 25:
        base_kpi = {"action": "normal_irrigation", "level": 2, "description": f"Temperatura normal ({temperature}°C)"}
    elif 25 <= temperature < 30:
        base_kpi = {"action": "intense_irrigation", "level": 3, "description": f"Temperatura alta ({temperature}°C)"}
    else:
        base_kpi = {"action": "maximum_irrigation", "level": 4, "description": f"Temperatura muy alta ({temperature}°C)"}
    
    if humidity < 40 and base_kpi['level'] > 0:
        base_kpi['level'] = min(base_kpi['level'] + 1, 4)
        base_kpi['description'] += f", ajustado por baja humedad ({humidity}%)"
    elif humidity > 70 and base_kpi['level'] > 0:
        base_kpi['level'] = max(base_kpi['level'] - 1, 0)
        base_kpi['description'] += f", ajustado por alta humedad ({humidity}%)"
    else:
        base_kpi['description'] += f", humedad normal ({humidity}%)"
    return base_kpi

def save_kpi_to_mongo(sensor_time, temperature, humidity, kpi_data):
    """Loads the calculated KPI into MongoDB."""
    try:
        client_mongo = MongoClient(config.MONGO_DB_URL)
        db = client_mongo[config.MONGO_IRRIGATION_DB]
        collection = db[config.MONGO_IRRIGATION_COLLECTION]
        document = {
            "timestamp": datetime.now(),
            "sensor_time_index": sensor_time,
            "temperature": temperature,
            "humidity": humidity,
            "kpi": kpi_data,
            "processed": True
        }
        result = collection.insert_one(document)
        client_mongo.close()
        print(f"Irrigation KPI saved to MongoDB with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error saving KPI to MongoDB: {e}")
        return None

def etl_process_irrigation():
    """Runs the complete ETL process for irrigation data."""
    print(f"\n[{datetime.now()}] --- Starting Irrigation ETL Process ---")
    sensor_data = get_last_irrigation_data()
    if not sensor_data:
        print("Irrigation ETL Stop: Could not get sensor data.")
        return
    print(f"  EXTRACT (Irrigation): Latest data is {sensor_data['temperature']}°C and {sensor_data['humidity']}% humidity")
    kpi = calculate_kpi(sensor_data['temperature'], sensor_data['humidity'])
    print(f"  TRANSFORM (Irrigation): Calculated KPI is '{kpi['action']}' (level {kpi['level']})")
    save_id = save_kpi_to_mongo(sensor_data['time_index'], sensor_data['temperature'], sensor_data['humidity'], kpi)
    if save_id:
        print("  LOAD (Irrigation): Successfully loaded data to MongoDB.")
    else:
        print("ETL Error (Irrigation): Failed to load data to MongoDB.")
    print("--- Irrigation ETL Process Finished ---")
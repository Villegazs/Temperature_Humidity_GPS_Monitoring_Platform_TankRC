"""
Stores all configuration variables for the application.
"""
# --- Database Configuration ---
CRATE_DB_URL = "http://crate-db:4200"
MONGO_DB_URL = "mongodb://mongo-db:27017/"

# -- Irrigation Service Config --
MONGO_IRRIGATION_DB = "sprinkler_db"
MONGO_IRRIGATION_COLLECTION = "riego_kpi"

# -- GPS Service Config --
MONGO_GPS_DB = "gps_db"
MONGO_GPS_COLLECTION = "location_history"

# --- Retry Settings ---
MAX_RETRIES = 5
RETRY_DELAY = 10  # seconds
MONGO_MAX_RETRIES = 5
MONGO_RETRY_DELAY = 10  # seconds

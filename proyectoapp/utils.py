"""
Contains shared utility functions used across the application,
like waiting for database connections.
"""
import time
from pymongo import MongoClient
from crate import client
import config

def wait_for_crate():
    """Waits for CrateDB to become available."""
    print("Waiting for CrateDB...")
    for i in range(1, config.MAX_RETRIES + 1):
        try:
            with client.connect(config.CRATE_DB_URL) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
            print("✓ CrateDB is available!")
            return True
        except Exception as e:
            print(f"Attempt {i}/{config.MAX_RETRIES}: CrateDB not yet available... ({e})")
            if i < config.MAX_RETRIES:
                time.sleep(config.RETRY_DELAY)
    print("⚠️ Could not connect to CrateDB after multiple attempts.")
    return False

def wait_for_mongo():
    """Waits for MongoDB to become available."""
    print("Waiting for MongoDB...")
    for i in range(1, config.MONGO_MAX_RETRIES + 1):
        try:
            client_mongo = MongoClient(config.MONGO_DB_URL, serverSelectionTimeoutMS=5000)
            client_mongo.admin.command("ping")
            client_mongo.close()
            print("✓ MongoDB is available!")
            return True
        except Exception as e:
            print(f"Attempt {i}/{config.MONGO_MAX_RETRIES}: MongoDB not yet available... ({e})")
            if i < config.MONGO_MAX_RETRIES:
                time.sleep(config.MONGO_RETRY_DELAY)
    print("⚠️ Could not connect to MongoDB after multiple attempts.")
    return False

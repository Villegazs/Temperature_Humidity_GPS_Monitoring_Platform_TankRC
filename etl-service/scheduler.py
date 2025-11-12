"""
Handles the setup and execution of scheduled background tasks (ETL processes).
Each scheduler runs in its own thread.
"""
import threading
import schedule
import time
from services.irrigation_service import etl_process_irrigation
from services.gps_service import etl_process_gps

def run_scheduler_irrigation():
    """Schedules the Irrigation ETL process to run every 5 minutes."""
    schedule.every(5).minutes.do(etl_process_irrigation)
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_scheduler_gps():
    """Schedules the GPS ETL process to run every 1 minute."""
    schedule.every(1).minutes.do(etl_process_gps)
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_schedulers():
    """Starts all schedulers in separate daemon threads."""
    irrigation_thread = threading.Thread(target=run_scheduler_irrigation, daemon=True)
    irrigation_thread.start()
    print("✓ Irrigation ETL scheduler started - will run every 5 minutes.")
    
    gps_thread = threading.Thread(target=run_scheduler_gps, daemon=True)
    gps_thread.start()
    print("✓ GPS ETL scheduler started - will run every 1 minute.")
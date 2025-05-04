# worker.py
from modules.reminder_scheduler import scheduler
from modules.db import init_db
init_db()

print("🔁 Background reminder scheduler started...")
# Keep the scheduler alive
import time
while True:
    time.sleep(60)

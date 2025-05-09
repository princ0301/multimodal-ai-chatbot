import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()
import certifi

try:
    client = MongoClient(
        os.environ["MONGODB_URI"],
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000
    )
    db = client["MediAlertDB"]
    reminders_collection = db["reminders"]
    users_collection = db["users"]
    print("✅ MongoDB connection successful on Render")

except Exception as e:
    print("❌ MongoDB connection failed:", e)

# def init_db():
#     pass

def insert_reminder(email, med, time_obj):
    reminders_collection.insert_one({
        "email": email,
        "med": med,
        "time": time_obj,
        "sent": False
    })

def get_pending_reminders():
    return list(reminders_collection.find({"sent": False}))

def mark_reminder_sent(reminder_id):
    reminders_collection.update_one(
        {"_id": ObjectId(reminder_id)},
        {"$set": {"sent": True}}
    )
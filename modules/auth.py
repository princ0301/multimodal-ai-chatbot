from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["MediAlertAuth"]
user_collection = db["users"]

def register_user(email, password):
    if user_collection.find_one({"email": email}):
        return False, "Email already exists"
    
    hashed_password = generate_password_hash(password)
    user_collection.insert_one({"email": email, "password": hashed_password})
    return True, "User registered successfully"

def verify_user(email, password):
    user = user_collection.find_one({"email": email})
    if user and check_password_hash(user["password"], password):
        return True
    return False


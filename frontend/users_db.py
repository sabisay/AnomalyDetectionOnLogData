import json
import os
from passlib.hash import bcrypt

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Eğer dosya yoksa varsayılan admin ve analyst tanımla
    return {
        "admin": {
            "password": bcrypt.hash("test123"),
            "role": "admin"
        },
        "analyst": {
            "password": bcrypt.hash("test123"),
            "role": "analyst"
        }
    }

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

users = load_users()
SECRET_KEY = "very-secret-key"

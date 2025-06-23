from passlib.hash import bcrypt

# Şifreler hashlenmiş olarak tutulur
users = {
    "admin": {
        "password": bcrypt.hash("test123"),
        "role": "admin"
    },
    "analyst": {
        "password": bcrypt.hash("test123"),
        "role": "analyst"
    }
}

# JWT için gizli anahtar
SECRET_KEY = "very-secret-key"

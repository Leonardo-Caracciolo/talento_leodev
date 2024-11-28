import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../data/data.db")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "user@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "password")
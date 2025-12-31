import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
SECRET_KEY = os.environ.get("SECRET_KEY", "a-very-secret-key")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
ENV = os.environ.get("ENV", "dev")
IS_PROD = ENV == "prod"

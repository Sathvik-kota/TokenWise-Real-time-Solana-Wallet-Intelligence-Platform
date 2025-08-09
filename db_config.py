import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Database configuration (local by default, can be overridden by env vars)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "transactions")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password") 
DB_PORT = int(os.getenv("DB_PORT", 5432))

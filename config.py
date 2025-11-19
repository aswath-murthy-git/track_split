"""
Configuration loader for environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'

if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from: {env_path}")
else:
    print(f"⚠️  No .env file found at: {env_path}")

# Email Configuration
SMTP_CONFIG = {
    'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'email': os.getenv('SMTP_EMAIL', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
}

# App Configuration
APP_CONFIG = {
    'secret_key': os.getenv('SECRET_KEY', 'change-this-secret-key-in-production'),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
}

def validate_email_config():
    """Validate email configuration"""
    if not SMTP_CONFIG['email'] or not SMTP_CONFIG['password']:
        print("⚠️  WARNING: Email credentials not configured in .env file")
        return False
    print("✅ Email configuration validated")
    return True
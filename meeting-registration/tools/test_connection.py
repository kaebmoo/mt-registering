#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Test 1: Check .env file
print("=" * 50)
print("1. Checking .env file...")
env_file = Path('.env')
if env_file.exists():
    print(f"✅ .env file found at: {env_file.absolute()}")
else:
    print(f"❌ .env file NOT found at: {env_file.absolute()}")

# Test 2: Load .env manually
print("\n" + "=" * 50)
print("2. Loading .env file...")
from dotenv import load_dotenv
result = load_dotenv()
print(f"Load .env result: {result}")

# Test 3: Check environment variables
print("\n" + "=" * 50)
print("3. Environment variables:")
env_vars = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']
for var in env_vars:
    value = os.environ.get(var)
    if var == 'POSTGRES_PASSWORD' and value:
        print(f"{var}: {'*' * len(value)}")
    else:
        print(f"{var}: {value}")

# Test 4: Build database URL
print("\n" + "=" * 50)
print("4. Database URL:")
from config import Config
config = Config()
print(f"DATABASE_URL: {config.DATABASE_URL}")
print(f"SQLALCHEMY_DATABASE_URI: {config.SQLALCHEMY_DATABASE_URI}")

# Test 5: Test psycopg2 connection directly
print("\n" + "=" * 50)
print("5. Testing direct psycopg2 connection...")
import psycopg2

try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
        database=os.environ.get('POSTGRES_DB', 'meeting_registration'),
        user=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'password')
    )
    print("✅ Direct connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Direct connection failed: {e}")

# Test 6: Test Flask app config
print("\n" + "=" * 50)
print("6. Testing Flask app configuration...")
from app import create_app

app = create_app('development')
with app.app_context():
    print(f"App DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"App POSTGRES_PORT: {app.config.get('POSTGRES_PORT')}")
    
    # Try to connect
    from models import db
    try:
        db.engine.connect()
        print("✅ Flask SQLAlchemy connection successful!")
    except Exception as e:
        print(f"❌ Flask SQLAlchemy connection failed: {e}")
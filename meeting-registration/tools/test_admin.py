#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

import os

print("=" * 50)
print("Admin Configuration Check")
print("=" * 50)

# Check environment variables
admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin2024')

print(f"ADMIN_USERNAME from env: {os.environ.get('ADMIN_USERNAME')}")
print(f"ADMIN_PASSWORD from env: {os.environ.get('ADMIN_PASSWORD')}")
print()
print(f"Final ADMIN_USERNAME: {admin_user}")
print(f"Final ADMIN_PASSWORD: {admin_pass}")
print()
print("Try login with these credentials:")
print(f"  Username: {admin_user}")
print(f"  Password: {admin_pass}")
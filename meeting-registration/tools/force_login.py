#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app('development')

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['admin_logged_in'] = True
    
    # Now try to access admin
    response = client.get('/admin/')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin access successful!")
    else:
        print("❌ Still redirecting...")
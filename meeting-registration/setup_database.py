#!/usr/bin/env python
"""Setup database safely - keeping existing data"""

import os
import sys

# Set environment before importing app
os.environ['FLASK_ENV'] = 'development'

# Import models directly without creating app
from models import db, Employee, Meeting, Registration
from config import config

def setup_database_safe():
    """Create only missing tables - preserve existing data"""
    
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    # Create minimal app just for database
    app = Flask(__name__)
    app.config.from_object(config['development'])
    
    # Initialize db with this app
    db.init_app(app)
    
    with app.app_context():
        print("🔍 Checking existing tables...")
        
        # ตรวจสอบตารางที่มีอยู่
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"\n📊 Existing tables: {existing_tables}")
        
        # สร้างเฉพาะตารางที่ยังไม่มี
        db.create_all()
        
        # ตรวจสอบตารางใหม่
        new_tables = inspector.get_table_names()
        added_tables = set(new_tables) - set(existing_tables)
        
        if added_tables:
            print(f"\n✅ New tables created: {list(added_tables)}")
        else:
            print("\n✅ No new tables needed")
        
        # ตรวจสอบข้อมูลเดิม
        try:
            emp_count = Employee.query.count()
            meeting_count = Meeting.query.count()
            reg_count = Registration.query.count()
            
            print(f"\n📈 Existing data preserved:")
            print(f"  - Employees: {emp_count}")
            print(f"  - Meetings: {meeting_count}")
            print(f"  - Registrations: {reg_count}")
        except Exception as e:
            print(f"Note: Some tables might be new: {e}")
        
        return True

if __name__ == "__main__":
    setup_database_safe()
import csv
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file FIRST
from dotenv import load_dotenv

# Try to load .env from current directory or parent directory
env_path = Path('.') / '.env'
if not env_path.exists():
    env_path = Path('..') / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment from {env_path}")
else:
    print("   Warning: .env file not found, using default values")
    print("   Create .env file from .env.example:")
    print("   cp .env.example .env")

# Now import app after env is loaded
from app import create_app
from models import db, Employee, Meeting

def test_database_connection():
    """Test database connection before importing"""
    import psycopg2
    
    try:
        # Get database credentials from environment
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=os.environ.get('POSTGRES_PORT', '5432'),
            database=os.environ.get('POSTGRES_DB', 'meeting_registration'),
            user=os.environ.get('POSTGRES_USER', 'postgres'),
            password=os.environ.get('POSTGRES_PASSWORD', 'password')
        )
        conn.close()
        print("✅ Database connection successful")
        return True
    except psycopg2.OperationalError as e:
        print(f" Database connection failed: {e}")
        print("\nPlease check your database configuration:")
        print(f"  Host: {os.environ.get('POSTGRES_HOST', 'localhost')}")
        print(f"  Port: {os.environ.get('POSTGRES_PORT', '5432')}")
        print(f"  Database: {os.environ.get('POSTGRES_DB', 'meeting_registration')}")
        print(f"  User: {os.environ.get('POSTGRES_USER', 'postgres')}")
        print(f"  Password: {'*' * len(os.environ.get('POSTGRES_PASSWORD', 'password'))}")
        return False

def import_employees_from_csv(csv_file):
    """Import employees from CSV file to database"""
    
    # Test connection first
    if not test_database_connection():
        print("\n Cannot proceed without database connection")
        print("\nOptions:")
        print("1. Check if PostgreSQL is running")
        print("2. Update .env file with correct credentials")
        print("3. If using Docker: docker-compose up -d postgres")
        return False
    
    app = create_app('development')
    
    with app.app_context():
        # Create tables if they don't exist
        try:
            db.create_all()
            print(" Database tables ready")
        except Exception as e:
            print(f" Error creating tables: {e}")
            return False
        
        imported = 0
        updated = 0
        errors = []
        
        try:
            # Check if CSV file exists
            if not os.path.exists(csv_file):
                print(f" File not found: {csv_file}")
                return False
            
            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Verify required columns
                if reader.fieldnames:
                    print(f" Found columns: {', '.join(reader.fieldnames[:5])}...")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        emp_id = row.get('emp_id', '').strip()
                        if not emp_id:
                            continue
                        
                        # Check if employee exists
                        employee = Employee.query.filter_by(emp_id=emp_id).first()
                        
                        if employee:
                            # Update existing employee
                            employee.emp_name = row.get('emp_name', '').strip()
                            employee.position = row.get('position', '').strip()
                            employee.section_code = row.get('รหัสส่วน', '').strip()
                            employee.sec_short = row.get('sec_short', '').strip()
                            employee.section_full = row.get('ส่วนเต็ม', '').strip()
                            employee.department_code = row.get('รหัสฝ่าย', '').strip()
                            employee.department_short = row.get('ฝ่ายย่อ', '').strip()
                            employee.department_full = row.get('ฝ่ายเต็ม', '').strip()
                            employee.group_code = row.get('รหัสกลุ่ม', '').strip()
                            employee.group_short = row.get('กลุ่มย่อ', '').strip()
                            employee.group_full = row.get('กลุ่มเต็ม', '').strip()
                            employee.division_code = row.get('รหัสสายงาน', '').strip()
                            employee.division_short = row.get('สายงานย่อ', '').strip()
                            employee.division_full = row.get('สายงานเต็ม', '').strip()
                            employee.cost_center_code = row.get('ศูนย์ต้นทุน', '').strip()
                            employee.cc_name = row.get('cc_name', '').strip()
                            updated += 1
                        else:
                            # Create new employee
                            employee = Employee(
                                emp_id=emp_id,
                                emp_name=row.get('emp_name', '').strip(),
                                position=row.get('position', '').strip(),
                                section_code=row.get('รหัสส่วน', '').strip(),
                                sec_short=row.get('sec_short', '').strip(),
                                section_full=row.get('ส่วนเต็ม', '').strip(),
                                department_code=row.get('รหัสฝ่าย', '').strip(),
                                department_short=row.get('ฝ่ายย่อ', '').strip(),
                                department_full=row.get('ฝ่ายเต็ม', '').strip(),
                                group_code=row.get('รหัสกลุ่ม', '').strip(),
                                group_short=row.get('กลุ่มย่อ', '').strip(),
                                group_full=row.get('กลุ่มเต็ม', '').strip(),
                                division_code=row.get('รหัสสายงาน', '').strip(),
                                division_short=row.get('สายงานย่อ', '').strip(),
                                division_full=row.get('สายงานเต็ม', '').strip(),
                                cost_center_code=row.get('ศูนย์ต้นทุน', '').strip(),
                                cc_name=row.get('cc_name', '').strip()
                            )
                            db.session.add(employee)
                            imported += 1
                        
                        # Commit every 100 records
                        if (imported + updated) % 100 == 0:
                            db.session.commit()
                            print(f"  Processed {imported + updated} records...")
                            
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        if len(errors) > 10:  # Stop if too many errors
                            break
                        continue
                
                # Final commit
                db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            print(f" Error reading CSV file: {e}")
            return False
        
        print(f"\n Import completed:")
        print(f"   - New employees imported: {imported}")
        print(f"   - Existing employees updated: {updated}")
        print(f"   - Total in database: {Employee.query.count()}")
        
        if errors:
            print(f"\n  Errors encountered: {len(errors)}")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   {error}")
        
        return True


def import_meeting_from_json(json_file):
    """Import meeting data from JSON file"""
    
    # Test connection first
    if not test_database_connection():
        print("\n Cannot proceed without database connection")
        return False
    
    app = create_app('development')
    
    with app.app_context():
        try:
            db.create_all()
            
            # Check if JSON file exists
            if not os.path.exists(json_file):
                print(f" File not found: {json_file}")
                return False
            
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            print(f" Loading meeting: {data.get('topic', 'Unknown')}")
            
            # Deactivate all existing meetings
            Meeting.query.update({Meeting.is_active: False})
            
            # Parse Thai date format
            thai_months = {
                'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4,
                'พ.ค.': 5, 'มิ.ย.': 6, 'ก.ค.': 7, 'ส.ค.': 8,
                'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12
            }
            
            date_parts = data['date'].split()
            day = int(date_parts[0])
            month = thai_months.get(date_parts[1], 1)
            year = int(date_parts[2]) - 543  # Convert Buddhist to Gregorian year
            
            meeting_date = datetime(year, month, day).date()
            
            # Parse time
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            
            # Create new meeting
            meeting = Meeting(
                topic=data['topic'],
                meeting_date=meeting_date,
                start_time=start_time,
                end_time=end_time,
                room=data.get('room', ''),
                floor=data.get('floor', ''),
                building=data.get('building', ''),
                is_active=True
            )
            
            db.session.add(meeting)
            db.session.commit()
            
            print(f"\n Meeting imported successfully:")
            print(f"   Topic: {meeting.topic}")
            print(f"   Date: {meeting.meeting_date}")
            print(f"   Time: {meeting.start_time} - {meeting.end_time}")
            print(f"   Location: Room {meeting.room}, Floor {meeting.floor}, {meeting.building}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f" Error importing meeting: {e}")
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Import data to registration system')
    parser.add_argument('--employees', help='Path to employees CSV file')
    parser.add_argument('--meeting', help='Path to meeting JSON file')
    parser.add_argument('--test', action='store_true', help='Test database connection only')
    
    args = parser.parse_args()
    
    if args.test:
        print("Testing database connection...")
        if test_database_connection():
            print(" Connection test successful!")
        else:
            print(" Connection test failed!")
        sys.exit(0)
    
    success = True
    
    if args.employees:
        print(f"\n Importing employees from {args.employees}...")
        if not import_employees_from_csv(args.employees):
            success = False
    
    if args.meeting:
        print(f"\n Importing meeting from {args.meeting}...")
        if not import_meeting_from_json(args.meeting):
            success = False
    
    if not args.employees and not args.meeting:
        print("Usage:")
        print("  python import_data.py --employees employee.csv")
        print("  python import_data.py --meeting schedule.json")
        print("  python import_data.py --employees employee.csv --meeting schedule.json")
        print("  python import_data.py --test  # Test database connection")
        print("\nMake sure .env file exists with database credentials")
        success = False
    
    sys.exit(0 if success else 1)

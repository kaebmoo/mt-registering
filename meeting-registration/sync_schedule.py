"""
Auto-sync meeting schedule from JSON file to database
Run this as a scheduled task (cron) to keep database updated
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from app import create_app
from models import db, Meeting

def sync_schedule_from_json(json_file='schedule.json'):
    """
    Sync meeting data from JSON file to database
    This can be run periodically to update meeting information
    """
    app = create_app('production')
    
    with app.app_context():
        # Check if JSON file exists
        if not os.path.exists(json_file):
            print(f"Warning: {json_file} not found")
            return False
        
        try:
            # Read JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse Thai date format
            thai_months = {
                'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4,
                'พ.ค.': 5, 'มิ.ย.': 6, 'ก.ค.': 7, 'ส.ค.': 8,
                'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12
            }
            
            date_parts = data['date'].split()
            day = int(date_parts[0])
            month = thai_months.get(date_parts[1], 1)
            year = int(date_parts[2]) - 543  # Convert Buddhist year to Gregorian
            
            meeting_date = datetime(year, month, day).date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            
            # Check if meeting with same topic and date exists
            existing_meeting = Meeting.query.filter_by(
                topic=data['topic'],
                meeting_date=meeting_date
            ).first()
            
            if existing_meeting:
                # Update existing meeting
                existing_meeting.start_time = start_time
                existing_meeting.end_time = end_time
                existing_meeting.room = data['room']
                existing_meeting.floor = data['floor']
                existing_meeting.building = data['building']
                existing_meeting.is_active = True
                
                # Deactivate other meetings
                Meeting.query.filter(Meeting.id != existing_meeting.id).update(
                    {Meeting.is_active: False}
                )
                
                print(f"✅ Updated existing meeting: {existing_meeting.topic}")
            else:
                # Deactivate all other meetings
                Meeting.query.update({Meeting.is_active: False})
                
                # Create new meeting
                new_meeting = Meeting(
                    topic=data['topic'],
                    meeting_date=meeting_date,
                    start_time=start_time,
                    end_time=end_time,
                    room=data['room'],
                    floor=data['floor'],
                    building=data['building'],
                    is_active=True
                )
                
                db.session.add(new_meeting)
                print(f"✅ Created new meeting: {new_meeting.topic}")
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error syncing schedule: {e}")
            return False

def watch_schedule_file(json_file='schedule.json', check_interval=60):
    """
    Watch for changes in schedule.json and auto-sync
    Run this as a background service
    """
    import time
    
    last_modified = None
    
    print(f"👁️ Watching {json_file} for changes...")
    
    while True:
        try:
            if os.path.exists(json_file):
                current_modified = os.path.getmtime(json_file)
                
                if last_modified is None or current_modified != last_modified:
                    print(f"📝 Change detected in {json_file}")
                    if sync_schedule_from_json(json_file):
                        print(f"✅ Successfully synced at {datetime.now()}")
                    last_modified = current_modified
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\n👋 Stopping schedule watcher")
            break
        except Exception as e:
            print(f"❌ Error in watcher: {e}")
            time.sleep(check_interval)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync meeting schedule from JSON')
    parser.add_argument('--watch', action='store_true', help='Watch for file changes')
    parser.add_argument('--file', default='schedule.json', help='JSON file path')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    if args.watch:
        # Run watcher
        watch_schedule_file(args.file, args.interval)
    else:
        # Run once
        if sync_schedule_from_json(args.file):
            print("✅ Schedule synced successfully")
        else:
            print("❌ Failed to sync schedule")

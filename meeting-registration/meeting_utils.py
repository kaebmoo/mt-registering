"""
Utility functions for reading meeting data from JSON file
"""

import json
import os
from datetime import datetime

def read_meeting_from_json(json_file='schedule.json'):
    """
    Read meeting data from JSON file (PHP-style)
    Returns dict with meeting information or None if file not found
    """
    if not os.path.exists(json_file):
        return None
    
    try:
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
        year = int(date_parts[2]) - 543
        
        # Format for display
        formatted_date = f"{day}/{month:02d}/{year}"
        
        return {
            'topic': data['topic'],
            'date': formatted_date,
            'date_thai': data['date'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'room': data['room'],
            'floor': data['floor'],
            'building': data['building']
        }
    except Exception as e:
        print(f"Error reading schedule.json: {e}")
        return None

def get_active_meeting_hybrid():
    """
    Get active meeting from database or JSON file
    Priority: Database > JSON file
    """
    from models import Meeting
    
    # First try database
    db_meeting = Meeting.get_active_meeting()
    if db_meeting:
        return db_meeting
    
    # Fallback to JSON file
    json_meeting = read_meeting_from_json()
    if json_meeting:
        # Create a mock Meeting object for template compatibility
        class MockMeeting:
            def __init__(self, data):
                self.topic = data['topic']
                self.meeting_date = type('obj', (object,), {
                    'strftime': lambda self, fmt: data['date']
                })()
                self.start_time = type('obj', (object,), {
                    'strftime': lambda self, fmt: data['start_time']
                })()
                self.end_time = type('obj', (object,), {
                    'strftime': lambda self, fmt: data['end_time']  
                })()
                self.room = data['room']
                self.floor = data['floor']
                self.building = data['building']
                self.id = 'json_meeting'  # Special ID for JSON-based meeting
        
        return MockMeeting(json_meeting)
    
    return None

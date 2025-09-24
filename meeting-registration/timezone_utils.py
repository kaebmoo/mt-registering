# timezone_utils.py - สร้างไฟล์ใหม่ในโปรเจค

import pytz
from datetime import datetime

def convert_to_timezone(dt, timezone='Asia/Bangkok'):
    """Convert UTC datetime to specific timezone"""
    if dt is None:
        return None
    
    # ถ้า datetime ไม่มี timezone info ให้ถือว่าเป็น UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    # แปลงเป็น timezone ที่ต้องการ
    tz = pytz.timezone(timezone)
    return dt.astimezone(tz)

def format_datetime_thai(dt, timezone='Asia/Bangkok', format='%d/%m/%Y %H:%M:%S'):
    """Format datetime to Thai timezone and format"""
    if dt is None:
        return ''
    
    # แปลง timezone
    local_dt = convert_to_timezone(dt, timezone)
    
    # Format ตามที่ต้องการ
    return local_dt.strftime(format)

def format_time_thai(dt, timezone='Asia/Bangkok'):
    """Format time only in Thai timezone"""
    return format_datetime_thai(dt, timezone, '%H:%M:%S')

def format_date_thai(dt, timezone='Asia/Bangkok'):
    """Format date only in Thai timezone"""
    return format_datetime_thai(dt, timezone, '%d/%m/%Y')
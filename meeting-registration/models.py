# meeting-registration/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from extensions import cache
from sqlalchemy.exc import OperationalError
import time
import logging
from flask import current_app

logger = logging.getLogger(__name__)
db = SQLAlchemy()

class Employee(db.Model):
    """Employee model for storing employee information"""
    __tablename__ = 'employees'
    
    emp_id = db.Column(db.String(20), primary_key=True)
    emp_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255))
    section_code = db.Column(db.String(50))
    sec_short = db.Column(db.String(100))
    section_full = db.Column(db.String(255))
    department_code = db.Column(db.String(50))
    department_short = db.Column(db.String(100))
    department_full = db.Column(db.String(255))
    group_code = db.Column(db.String(50))
    group_short = db.Column(db.String(100))
    group_full = db.Column(db.String(255))
    division_code = db.Column(db.String(50))
    division_short = db.Column(db.String(100))
    division_full = db.Column(db.String(255))
    cost_center_code = db.Column(db.String(50))
    cc_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('Registration', backref='employee', lazy='dynamic')
    
    def __repr__(self):
        return f'<Employee {self.emp_id}: {self.emp_name}>'
    
    def to_dict(self):
        """Convert employee object to dictionary"""
        return {
            'emp_id': self.emp_id,
            'emp_name': self.emp_name,
            'position': self.position,
            'sec_short': self.sec_short,
            'cc_name': self.cc_name
        }
    
    @classmethod
    def search_by_id(cls, emp_id):
        """Search employee by ID with various formats"""
        max_retries = current_app.config.get('DATABASE_RETRY_COUNT', 3)
        retry_delay = current_app.config.get('DATABASE_RETRY_DELAY', 1)
        
        for attempt in range(max_retries):
            try:
                emp_id = str(emp_id).strip()
                
                # ค้นหาแบบตรงกัน
                employee = cls.query.filter_by(emp_id=emp_id).first()
                if employee:
                    return employee
                
                # ลอง trim leading zeros
                emp_id_no_leading = emp_id.lstrip('0')
                if len(emp_id_no_leading) >= 6:
                    employee = cls.query.filter_by(emp_id=emp_id_no_leading).first()
                    if employee:
                        return employee
                
                # ลองเติม 0 ข้างหน้าให้ครบ 8 หลัก
                if len(emp_id) < 8:
                    emp_id_padded = emp_id.zfill(8)
                    employee = cls.query.filter_by(emp_id=emp_id_padded).first()
                    if employee:
                        return employee
                
                return None
                
            except OperationalError as e:
                logger.warning(f"Database error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    try:
                        db.session.rollback()
                        db.session.remove()
                        time.sleep(retry_delay * (attempt + 1))
                    except:
                        pass
                else:
                    logger.error(f"Failed after {max_retries} attempts")
                    return None
        
        return None


class Meeting(db.Model):
    """Meeting model for storing meeting information"""
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.Text, nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(100))
    floor = db.Column(db.String(50))
    building = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('Registration', backref='meeting', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Meeting {self.id}: {self.topic}>'
    
    def to_dict(self):
        """Convert meeting object to dictionary"""
        return {
            'id': self.id,
            'topic': self.topic,
            'meeting_date': self.meeting_date.strftime('%Y-%m-%d'),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'room': self.room,
            'floor': self.floor,
            'building': self.building,
            'is_active': self.is_active
        }
    
    @classmethod
    @cache.cached(timeout=60, key_prefix='active_meeting')
    def get_active_meeting(cls):
        """Get the currently active meeting (cached for 60 seconds)"""
        max_retries = current_app.config.get('DATABASE_RETRY_COUNT', 3)
        retry_delay = current_app.config.get('DATABASE_RETRY_DELAY', 1)

        for attempt in range(max_retries):
            try:
                logger.debug(f"Fetching active meeting from DB (attempt {attempt + 1})")
                result = cls.query.filter_by(is_active=True).order_by(cls.created_at.desc()).first()
                return result
            except OperationalError as e:
                logger.warning(f"Database connection error on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    # Try to reconnect
                    try:
                        db.session.rollback()
                        db.session.remove()
                        time.sleep(retry_delay * (attempt + 1))
                    except:
                        pass
                else:
                    # Clear cache on final failure
                    cache.delete('active_meeting')
                    logger.error(f"Failed to get active meeting after {max_retries} attempts")
                    return None
        
        return None


class Registration(db.Model):
    """Registration model for storing registration information"""
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    emp_id = db.Column(db.String(20), db.ForeignKey('employees.emp_id', ondelete='SET NULL'))
    emp_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255))
    sec_short = db.Column(db.String(100))
    cc_name = db.Column(db.String(255))
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_manual_entry = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (
        UniqueConstraint('meeting_id', 'emp_id', name='unique_meeting_employee'),
        Index('idx_registration_time', 'registration_time'),
    )
    
    def __repr__(self):
        return f'<Registration {self.id}: {self.emp_name} for Meeting {self.meeting_id}>'
    
    def to_dict(self):
        """Convert registration object to dictionary"""
        return {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'emp_id': self.emp_id,
            'emp_name': self.emp_name,
            'position': self.position,
            'sec_short': self.sec_short,
            'cc_name': self.cc_name,
            'registration_time': self.registration_time.isoformat(),
            'is_manual_entry': self.is_manual_entry
        }
    
    @classmethod
    def check_duplicate(cls, meeting_id, emp_id):
        """Check if registration already exists"""
        return cls.query.filter_by(
            meeting_id=meeting_id,
            emp_id=emp_id
        ).first() is not None

# meeting-registration/app.py

from dotenv import load_dotenv
load_dotenv()
    
import os
import json
from flask_caching import Cache
import requests
import logging
import pytz
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import OperationalError, DatabaseError, DisconnectionError
from sqlalchemy import event, text
from sqlalchemy.pool import Pool
import time
from werkzeug.middleware.proxy_fix import ProxyFix
from pathlib import Path

from config import config
from models import db, Employee, Meeting, Registration
from admin import admin_bp
from extensions import cache, celery_app
from timezone_utils import convert_to_timezone, format_datetime_thai, format_time_thai, format_date_thai


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory pattern"""

    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # Fix session configuration
    app.config['SESSION_COOKIE_NAME'] = 'meeting_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

    # Make sure SECRET_KEY is set
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    print(f"SECRET_KEY is set: {bool(app.config.get('SECRET_KEY'))}")
    print(f"Environment: {config_name}")
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    cache.init_app(app)
    
    # Configure Celery
    celery_app.config_from_object(app.config, namespace='CELERY')
    celery_app.conf.update(app.config)

    # Make tasks run within the app context
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery_app.Task = ContextTask

    # Setup ProxyFix for proper IP address detection behind proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Handle URL prefix configuration from environment variables
    app_root = os.environ.get('APPLICATION_ROOT', '')
    preferred_scheme = os.environ.get('PREFERRED_URL_SCHEME', '')
    
    if app_root:
        print(f"Setting APPLICATION_ROOT to: {app_root}")
        app.config['APPLICATION_ROOT'] = app_root
        
        # Custom middleware to handle SCRIPT_NAME
        class PrefixMiddleware:
            def __init__(self, app, prefix=''):
                self.app = app
                self.prefix = prefix

            def __call__(self, environ, start_response):
                # Log the incoming request for debugging (only in debug mode)
                if app.config.get('DEBUG'):
                    logger.info(f"Incoming PATH_INFO: {environ.get('PATH_INFO')}")
                    logger.info(f"Incoming SCRIPT_NAME: {environ.get('SCRIPT_NAME')}")
                
                # Set SCRIPT_NAME if not already set
                if self.prefix and not environ.get('SCRIPT_NAME'):
                    environ['SCRIPT_NAME'] = self.prefix
                    
                # Fix PATH_INFO if it starts with the prefix
                path = environ.get('PATH_INFO', '')
                if path.startswith(self.prefix):
                    environ['PATH_INFO'] = path[len(self.prefix):]
                    environ['SCRIPT_NAME'] = self.prefix
                    if app.config.get('DEBUG'):
                        logger.info(f"Fixed PATH_INFO: {environ.get('PATH_INFO')}")
                        logger.info(f"Fixed SCRIPT_NAME: {environ.get('SCRIPT_NAME')}")
                    
                return self.app(environ, start_response)
        
        # Apply the prefix middleware
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app_root)
    
    if preferred_scheme:
        print(f"Setting PREFERRED_URL_SCHEME to: {preferred_scheme}")
        app.config['PREFERRED_URL_SCHEME'] = preferred_scheme
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    )
    
    # Register blueprints
    app.register_blueprint(admin_bp)

    # The Celery task definition can stay here
    @celery_app.task(name='tasks.send_to_google_sheets')
    def send_to_google_sheets_task(registration_data, google_script_url):
        """Celery task to send registration data to Google Sheets."""
        if not google_script_url:
            return
        
        try:
            response = requests.post(
                google_script_url,
                json=registration_data,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Successfully sent data to Google Sheets for emp_id: {registration_data.get('รหัสพนักงาน')}")
        except Exception as e:
            logger.error(f"Error sending to Google Sheets: {e}")
    
    @app.before_request
    def before_request():
        """Set session lifetime and check for session validity"""
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=1)

    # Register template filters for timezone conversion
    @app.template_filter('to_timezone')
    def to_timezone_filter(dt, timezone=None):
        """Convert datetime to specified timezone"""
        if timezone is None:
            timezone = app.config.get('DISPLAY_TIMEZONE', 'Asia/Bangkok')
        return convert_to_timezone(dt, timezone)
    
    @app.template_filter('datetime_thai')
    def datetime_thai_filter(dt, format='%d/%m/%Y %H:%M:%S'):
        """Format datetime in Thai timezone"""
        timezone = app.config.get('DISPLAY_TIMEZONE', 'Asia/Bangkok')
        return format_datetime_thai(dt, timezone, format)
    
    @app.template_filter('time_thai')
    def time_thai_filter(dt):
        """Format time only in Thai timezone"""
        timezone = app.config.get('DISPLAY_TIMEZONE', 'Asia/Bangkok')
        return format_time_thai(dt, timezone)
    
    @app.template_filter('date_thai')
    def date_thai_filter(dt):
        """Format date only in Thai timezone"""
        timezone = app.config.get('DISPLAY_TIMEZONE', 'Asia/Bangkok')
        return format_date_thai(dt, timezone)
    
    # Context processor to inject timezone info
    @app.context_processor
    def inject_timezone():
        return {
            'timezone': app.config.get('DISPLAY_TIMEZONE', 'Asia/Bangkok'),
            'current_time_local': datetime.now(pytz.timezone(app.config.get('DISPLAY_TIMEZONE', 'Asia/Bangkok'))),
            'datetime': datetime
        }
    
    @app.route('/')
    def index():
        """Main registration page"""
        meeting = Meeting.get_active_meeting()
        if not meeting:
            flash('ไม่มีการประชุมที่เปิดให้ลงทะเบียน', 'warning')
        return render_template('index.html', meeting=meeting)
    
    @app.route('/submit', methods=['POST'])
    @limiter.limit("10 per minute")  # Rate limit to prevent spam
    def register():
        """Handle registration submission"""
        emp_id = request.form.get('emp_id', '').strip()
        
        if not emp_id:
            flash('กรุณากรอกรหัสพนักงาน', 'error')
            return redirect(url_for('index'))
        
        if len(emp_id) < 6:
            flash(f'รหัสพนักงานต้องมีอย่างน้อย 6 หลัก (คุณใส่ {len(emp_id)} หลัก)', 'error')
            return render_template('manual_registration.html', emp_id=emp_id)
        
        # Get active meeting
        meeting = Meeting.get_active_meeting()
        if not meeting:
            flash('ไม่มีการประชุมที่เปิดให้ลงทะเบียน', 'error')
            return redirect(url_for('index'))
        # บังคับให้ SQLAlchemy โหลดสถานะล่าสุดของ meeting object จาก DB
        # เพื่อล้างสถานะเก่าที่อาจค้างมาจาก Cache หรือ Session ก่อนหน้า
        # meeting = db.session.merge(cached_meeting)

        # Check for cooldown period (prevent rapid submissions)
        last_registration_key = f"last_reg_{get_remote_address()}"
        if last_registration_key in session:
            last_time = datetime.fromisoformat(session[last_registration_key])
            if datetime.now() - last_time < timedelta(seconds=app.config['REGISTRATION_COOLDOWN']):
                flash('กรุณารอสักครู่ก่อนลงทะเบียนใหม่', 'warning')
                return redirect(url_for('index'))
        
        # Search for employee
        employee = Employee.search_by_id(emp_id)
        
        if employee:
            # Check for duplicate registration
            if Registration.check_duplicate(meeting.id, employee.emp_id):
                flash('คุณได้ลงทะเบียนในการประชุมนี้แล้ว', 'info')
                return render_template('registration_success.html', 
                                     registration_data=employee.to_dict(),
                                     meeting=meeting,
                                     already_registered=True)
            
            try:
                # Create registration
                registration = Registration(
                    meeting_id=meeting.id,
                    emp_id=employee.emp_id,
                    emp_name=employee.emp_name,
                    position=employee.position,
                    sec_short=employee.sec_short,
                    cc_name=employee.cc_name,
                    is_manual_entry=False,
                    ip_address=get_remote_address(),
                    user_agent=request.headers.get('User-Agent', '')[:500]
                )
                
                db.session.add(registration)
                db.session.commit()
                
                # Update session with last registration time
                session[last_registration_key] = datetime.now().isoformat()
                
                # Send to Google Sheets (async)
                try:
                    # Create a dictionary of data for the task
                    reg_data_for_task = {
                        'รหัสพนักงาน': registration.emp_id,
                        'ชื่อ': registration.emp_name,
                        'ตำแหน่ง': registration.position or '',
                        'ส่วนงานย่อ': registration.sec_short or '',
                        'ชื่อศูนย์ต้นทุน': registration.cc_name or '',
                        'เวลาลงทะเบียน': registration.registration_time.isoformat(),
                        'ลงทะเบียนด้วยตนเอง': 'ใช่' if registration.is_manual_entry else 'ไม่ใช่'
                    }
                    # Call the Celery task asynchronously using .delay()
                    send_to_google_sheets_task.delay(reg_data_for_task, app.config['GOOGLE_SCRIPT_URL'])
                except Exception as e:
                    logger.error(f"Failed to queue task for Google Sheets: {e}")
                
                flash('ลงทะเบียนสำเร็จ', 'success')
                return render_template('registration_success.html', 
                                     registration_data=employee.to_dict(),
                                     meeting=meeting,
                                     already_registered=False)
                
            except IntegrityError:
                db.session.rollback()
                flash('คุณได้ลงทะเบียนในการประชุมนี้แล้ว', 'info')
                return render_template('registration_success.html', 
                                     registration_data=employee.to_dict(),
                                     meeting=meeting,
                                     already_registered=True)
            except Exception as e:
                db.session.rollback()
                logger.error(f"Registration error: {e}")
                flash('เกิดข้อผิดพลาดในการลงทะเบียน กรุณาลองใหม่', 'error')
                return redirect(url_for('index'))
        else:
            # Employee not found - show manual registration form
            return render_template('manual_registration.html', 
                                 emp_id=emp_id,
                                 meeting=meeting)
    
    @app.route('/submit_manual', methods=['POST'])
    @limiter.limit("5 per minute")
    def register_manual():
        """Handle manual registration submission"""
        meeting = Meeting.get_active_meeting()
        if not meeting:
            flash('ไม่มีการประชุมที่เปิดให้ลงทะเบียน', 'error')
            return redirect(url_for('index'))
        
        # ใช้ session.merge() เพื่อนำ object จาก cache กลับเข้าสู่ session ปัจจุบัน
        # ทำให้เราได้ object ตัวจริงที่ session กำลังดูแลอยู่
        # cached_meeting = Meeting.get_active_meeting()
        # if not cached_meeting:
        #     flash('ไม่มีการประชุมที่เปิดให้ลงทะเบียน', 'error')
        #     return redirect(url_for('index'))
        # meeting = db.session.merge(cached_meeting)

        # Get form data
        new_emp_id = request.form.get('new_emp_id', '').strip()
        new_emp_name = request.form.get('new_emp_name', '').strip()
        new_position = request.form.get('new_position', '').strip()
        new_sec_short = request.form.get('new_sec_short', '').strip()
        new_cc_name = request.form.get('new_cc_name', '').strip()
        
        # Validate
        if len(new_emp_id) < 6:
            flash('รหัสพนักงานต้องมีอย่างน้อย 6 หลัก', 'error')
            return render_template('manual_registration.html', 
                                 emp_id=new_emp_id,
                                 meeting=meeting)
        
        if not new_emp_name:
            flash('กรุณากรอกชื่อ-นามสกุล', 'error')
            return render_template('manual_registration.html', 
                                 emp_id=new_emp_id,
                                 meeting=meeting)
        
        # Check for duplicate
        if Registration.check_duplicate(meeting.id, new_emp_id):
            flash('รหัสพนักงานนี้ได้ลงทะเบียนในการประชุมนี้แล้ว', 'warning')
            return redirect(url_for('index'))
        
        try:
            # Create manual registration
            registration = Registration(
                meeting_id=meeting.id,
                emp_id=new_emp_id,
                emp_name=new_emp_name,
                position=new_position,
                sec_short=new_sec_short,
                cc_name=new_cc_name,
                is_manual_entry=True,
                ip_address=get_remote_address(),
                user_agent=request.headers.get('User-Agent', '')[:500]
            )
            
            db.session.add(registration)
            db.session.commit()
            
            # Send to Google Sheets (async)
            try:
                reg_data_for_task = {
                    'รหัสพนักงาน': registration.emp_id,
                    'ชื่อ': registration.emp_name,
                    'ตำแหน่ง': registration.position or '',
                    'ส่วนงานย่อ': registration.sec_short or '',
                    'ชื่อศูนย์ต้นทุน': registration.cc_name or '',
                    'เวลาลงทะเบียน': registration.registration_time.isoformat(),
                    'ลงทะเบียนด้วยตนเอง': 'ใช่' if registration.is_manual_entry else 'ไม่ใช่'
                }
                send_to_google_sheets_task.delay(reg_data_for_task, app.config['GOOGLE_SCRIPT_URL'])
            except Exception as e:
                logger.error(f"Failed to queue task for Google Sheets: {e}")
            
            flash('ลงทะเบียนด้วยตนเองสำเร็จ', 'success')
            return render_template('registration_success.html', 
                                 registration_data={
                                     'emp_id': new_emp_id,
                                     'emp_name': new_emp_name,
                                     'position': new_position,
                                     'sec_short': new_sec_short,
                                     'cc_name': new_cc_name
                                 },
                                 meeting=meeting,
                                 already_registered=False,
                                 is_manual=True)
            
        except IntegrityError:
            db.session.rollback()
            flash('รหัสพนักงานนี้ได้ลงทะเบียนในการประชุมนี้แล้ว', 'warning')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Manual registration error: {e}")
            flash('เกิดข้อผิดพลาดในการลงทะเบียน กรุณาลองใหม่', 'error')
            return redirect(url_for('index'))
    
    @app.route('/api/check_employee/<emp_id>')
    @limiter.limit("30 per minute")
    def check_employee(emp_id):
        """API endpoint to check if employee exists"""
        employee = Employee.search_by_id(emp_id)
        if employee:
            return jsonify({'exists': True, 'data': employee.to_dict()})
        return jsonify({'exists': False})
    
    @app.route('/api/registration_status/<meeting_id>/<emp_id>')
    def registration_status(meeting_id, emp_id):
        """Check registration status"""
        is_registered = Registration.check_duplicate(meeting_id, emp_id)
        return jsonify({'registered': is_registered})
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded"""
        flash('คุณส่งคำขอมากเกินไป กรุณารอสักครู่', 'warning')
        return redirect(url_for('index'))
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Database error handlers
    @event.listens_for(Pool, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Set connection parameters when connecting"""
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
            cursor = dbapi_conn.cursor()
            try:
                cursor.execute(text("SET statement_timeout = '30s'"))
                cursor.close()
            except:
                pass
    
    @app.errorhandler(OperationalError)
    def handle_db_error(error):
        """Handle database connection errors"""
        db.session.rollback()
        logger.error(f"Database error: {error}")
        flash('เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล กรุณาลองใหม่', 'error')
        return redirect(url_for('index'))
    
    def send_to_google_sheets(registration):
        """Send registration data to Google Sheets"""
        if not app.config.get('GOOGLE_SCRIPT_URL'):
            return
        
        data = {
            'รหัสพนักงาน': registration.emp_id,
            'ชื่อ': registration.emp_name,
            'ตำแหน่ง': registration.position or '',
            'ส่วนงานย่อ': registration.sec_short or '',
            'ชื่อศูนย์ต้นทุน': registration.cc_name or '',
            'เวลาลงทะเบียน': registration.registration_time.isoformat(),
            'ลงทะเบียนด้วยตนเอง': 'ใช่' if registration.is_manual_entry else 'ไม่ใช่'
        }
        
        try:
            response = requests.post(
                app.config['GOOGLE_SCRIPT_URL'],
                json=data,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error sending to Google Sheets: {e}")
            # Don't raise - this is not critical
    
    return app

# Create app instance for development
if __name__ == '__main__':
    import sys
    
    app = create_app('development')
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("Database connected successfully!")
            
            # Create tables if not exist
            db.create_all()
            print("Database tables created/verified!")

            # Test cache connection
            try:
                cache.set('test', 'ok', timeout=1)
                if cache.get('test') == 'ok':
                    print("Cache (Redis) connected successfully!")
                else:
                    print("Cache not working, using memory cache")
            except:
                print("Redis not available, using memory cache")
            
        except OperationalError as e:
            print("Database connection failed!")
            print(f"Error: {e}")
            print("\nPlease check:")
            print("1. PostgreSQL is running")
            print("2. Database credentials in .env file")
            print("3. Database 'meeting_registration' exists")
            print("\nTry running:")
            print("  brew services start postgresql@14  # For macOS")
            print("  createdb meeting_registration      # Create database")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    
    # Start Flask app
    print(f"Starting Flask app on http://0.0.0.0:9000")
    app.run(host='0.0.0.0', port=9000, debug=True)
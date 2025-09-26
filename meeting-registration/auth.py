# auth.py - ใช้ email_service แทน Flask-Mail

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, OTPToken
from tasks import email_queue, send_otp_email_task
import os
import re
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def is_email_allowed(email):
    """Check if email domain is allowed"""
    allowed_domains = os.environ.get('ALLOWED_EMAIL_DOMAINS', '').split(',')
    if not allowed_domains or allowed_domains == ['']:
        return True  # ถ้าไม่ได้กำหนด = อนุญาตทั้งหมด
    
    domain = email.split('@')[1] if '@' in email else ''
    return domain in [d.strip() for d in allowed_domains]

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        
        # Validate email format
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('รูปแบบ email ไม่ถูกต้อง', 'error')
            return render_template('auth/register.html')
        
        # Check allowed domains
        if not is_email_allowed(email):
            flash('Email domain นี้ไม่ได้รับอนุญาต', 'error')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email นี้ลงทะเบียนแล้ว', 'error')
            return render_template('auth/register.html')
        
        # Generate OTP
        otp = OTPToken.generate_otp(email, purpose='register')
        
        try:
            # Queue email sending
            job = email_queue.enqueue(
                send_otp_email_task,
                recipient_email=email,
                recipient_name=name,
                otp=otp,
                purpose='register',
                job_timeout='5m'
            )
            
            # Store temp data in session
            session['register_email'] = email
            session['register_name'] = name
            session['email_job_id'] = job.id
            
            flash('กำลังส่ง OTP ไปยัง email ของคุณ กรุณารอสักครู่', 'info')
            return redirect(url_for('auth.verify_register'))
            
        except Exception as e:
            # Fallback: ถ้า RQ ไม่ทำงาน ให้ส่งโดยตรง
            from email_service import EmailService
            email_service = EmailService()
            if email_service.send_otp_email(email, name, otp, 'register'):
                session['register_email'] = email
                session['register_name'] = name
                flash('ส่ง OTP ไปยัง email ของคุณแล้ว', 'success')
                return redirect(url_for('auth.verify_register'))
            else:
                flash('ไม่สามารถส่ง email ได้ กรุณาลองใหม่', 'error')
                return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/verify-register', methods=['GET', 'POST'])
def verify_register():
    """Verify registration OTP"""
    email = session.get('register_email')
    if not email:
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        if OTPToken.verify_otp(email, otp, purpose='register'):
            # Create user
            user = User(
                email=email,
                name=session.get('register_name'),
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            
            # Clear session
            session.pop('register_email', None)
            session.pop('register_name', None)
            session.pop('email_job_id', None)
            
            # Auto login
            session['user_id'] = user.id
            session['user_email'] = user.email
            
            flash('ลงทะเบียนสำเร็จ', 'success')
            return redirect(url_for('organizer.dashboard'))
        else:
            flash('รหัส OTP ไม่ถูกต้องหรือหมดอายุ', 'error')
    
    return render_template('auth/verify_otp.html', email=email, purpose='register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login with email OTP"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        # Check if user exists
        user = User.query.filter_by(email=email, is_active=True).first()
        if not user:
            flash('ไม่พบ email นี้ในระบบ', 'error')
            return render_template('auth/login.html')
        
        # Generate OTP
        otp = OTPToken.generate_otp(email, purpose='login')
        
        try:
            # Queue email sending
            job = email_queue.enqueue(
                send_otp_email_task,
                recipient_email=email,
                recipient_name=user.name,
                otp=otp,
                purpose='login',
                job_timeout='5m'
            )
            
            session['login_email'] = email
            session['email_job_id'] = job.id
            
            flash('กำลังส่ง OTP ไปยัง email ของคุณ กรุณารอสักครู่', 'info')
            return redirect(url_for('auth.verify_login'))
            
        except Exception as e:
            # Fallback: ถ้า RQ ไม่ทำงาน ให้ส่งโดยตรง
            from email_service import EmailService
            email_service = EmailService()
            if email_service.send_otp_email(email, user.name, otp, 'login'):
                session['login_email'] = email
                flash('ส่ง OTP ไปยัง email ของคุณแล้ว', 'success')
                return redirect(url_for('auth.verify_login'))
            else:
                flash('ไม่สามารถส่ง email ได้ กรุณาลองใหม่', 'error')
                return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/verify-login', methods=['GET', 'POST'])
def verify_login():
    """Verify login OTP"""
    email = session.get('login_email')
    if not email:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        if OTPToken.verify_otp(email, otp, purpose='login'):
            user = User.query.filter_by(email=email).first()
            
            # Update last login
            user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
            db.session.commit()
            
            # Set session
            session.pop('login_email', None)
            session.pop('email_job_id', None)
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['is_admin'] = user.is_admin
            
            flash('เข้าสู่ระบบสำเร็จ', 'success')
            
            # Redirect based on role
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('organizer.dashboard'))
        else:
            flash('รหัส OTP ไม่ถูกต้องหรือหมดอายุ', 'error')
    
    return render_template('auth/verify_otp.html', email=email, purpose='login')

@auth_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('ออกจากระบบแล้ว', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/check-email-status')
def check_email_status():
    """Check email sending status (for AJAX)"""
    from rq.job import Job
    from tasks import email_queue
    
    job_id = session.get('email_job_id')
    if not job_id:
        return jsonify({'status': 'no_job'})
    
    try:
        job = Job.fetch(job_id, connection=email_queue.connection)
        return jsonify({
            'status': job.get_status(),
            'result': job.result
        })
    except:
        return jsonify({'status': 'not_found'})
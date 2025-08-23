import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask import session, send_file
from functools import wraps
import csv
import io
from sqlalchemy import func, desc
from models import db, Employee, Meeting, Registration
from extensions import cache

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simple authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('กรุณาเข้าสู่ระบบ', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.before_request
def inject_active_meeting():
    """Inject active meeting to all admin templates"""
    from flask import g
    g.active_meeting = Meeting.get_active_meeting()

@admin_bp.context_processor
def inject_template_vars():
    """Make variables available to all admin templates"""
    return {
        'active_meeting': Meeting.get_active_meeting()
    }

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication
        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
        ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin2024')
        
        # DEBUG
        # print(f"Login attempt - Username: {username}, Expected: {ADMIN_USERNAME}")
        # print(f"Password match: {password == ADMIN_PASSWORD}")
        # print(f"Session before: {session.get('admin_logged_in')}")
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            
            # DEBUG
            # print(f"Session after login: {session.get('admin_logged_in')}")
            # print(f"Session items: {dict(session)}")
            
            flash('เข้าสู่ระบบสำเร็จ', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('ออกจากระบบแล้ว', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard"""
    # DEBUG
    print(f"Dashboard - Session logged in: {session.get('admin_logged_in')}")
    print(f"Dashboard - Full session: {dict(session)}")

    # Get statistics
    total_employees = Employee.query.count()
    active_meeting = Meeting.get_active_meeting()
    
    stats = {
        'total_employees': total_employees,
        'total_meetings': Meeting.query.count(),
        'active_meeting': active_meeting
    }
    
    if active_meeting:
        stats['total_registrations'] = Registration.query.filter_by(
            meeting_id=active_meeting.id
        ).count()
        
        # Get recent registrations
        recent_registrations = Registration.query.filter_by(
            meeting_id=active_meeting.id
        ).order_by(desc(Registration.registration_time)).limit(10).all()
        
        # Registration by hour statistics
        hourly_stats = db.session.query(
            func.date_trunc('hour', Registration.registration_time).label('hour'),
            func.count(Registration.id).label('count')
        ).filter_by(meeting_id=active_meeting.id).group_by('hour').all()
        
        stats['recent_registrations'] = recent_registrations
        stats['hourly_stats'] = hourly_stats
    
    return render_template('admin/dashboard.html', **stats)

@admin_bp.route('/meetings')
@login_required
def meetings():
    """Manage meetings"""
    meetings = Meeting.query.order_by(desc(Meeting.created_at)).all()
    return render_template('admin/meetings.html', meetings=meetings)

@admin_bp.route('/meetings/create', methods=['GET', 'POST'])
@login_required
def create_meeting():
    """Create new meeting"""
    if request.method == 'POST':
        try:
            # Deactivate all other meetings
            Meeting.query.update({Meeting.is_active: False})
            
            meeting = Meeting(
                topic=request.form.get('topic'),
                meeting_date=datetime.strptime(request.form.get('meeting_date'), '%Y-%m-%d').date(),
                start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
                end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
                room=request.form.get('room'),
                floor=request.form.get('floor'),
                building=request.form.get('building'),
                is_active=True
            )
            
            db.session.add(meeting)
            db.session.commit()

            cache.delete('active_meeting')
            
            flash('สร้างการประชุมใหม่สำเร็จ', 'success')
            return redirect(url_for('admin.meetings'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return render_template('admin/create_meeting.html')

@admin_bp.route('/meetings/<int:meeting_id>/toggle')
@login_required
def toggle_meeting(meeting_id):
    """Toggle meeting active status"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.is_active:
        meeting.is_active = False
    else:
        # Deactivate all other meetings
        Meeting.query.update({Meeting.is_active: False})
        meeting.is_active = True
    
    db.session.commit()
    cache.delete('active_meeting')
    flash('อัปเดตสถานะการประชุมแล้ว', 'success')
    return redirect(url_for('admin.meetings'))

@admin_bp.route('/registrations/<int:meeting_id>')
@login_required
def view_registrations(meeting_id):
    """View registrations for a meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    registrations = Registration.query.filter_by(
        meeting_id=meeting_id
    ).order_by(desc(Registration.registration_time)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/registrations.html', 
                         meeting=meeting, 
                         registrations=registrations)

@admin_bp.route('/registrations/<int:meeting_id>/export')
@login_required
def export_registrations(meeting_id):
    """Export registrations to CSV"""
    meeting = Meeting.query.get_or_404(meeting_id)
    registrations = Registration.query.filter_by(meeting_id=meeting_id).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'ลำดับ', 'รหัสพนักงาน', 'ชื่อ-นามสกุล', 'ตำแหน่ง', 
        'ส่วนงานย่อ', 'ศูนย์ต้นทุน', 'เวลาลงทะเบียน', 'ลงทะเบียนด้วยตนเอง'
    ])
    
    # Write data
    for idx, reg in enumerate(registrations, 1):
        writer.writerow([
            idx,
            reg.emp_id or '',
            reg.emp_name,
            reg.position or '',
            reg.sec_short or '',
            reg.cc_name or '',
            reg.registration_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ใช่' if reg.is_manual_entry else 'ไม่ใช่'
        ])
    
    # Prepare response
    output.seek(0)
    output_bytes = io.BytesIO()
    output_bytes.write(output.getvalue().encode('utf-8-sig'))  # UTF-8 with BOM for Excel
    output_bytes.seek(0)
    
    filename = f"registrations_{meeting_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        output_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@admin_bp.route('/employees')
@login_required
def employees():
    """View employees"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Employee.query
    
    if search:
        query = query.filter(
            db.or_(
                Employee.emp_id.contains(search),
                Employee.emp_name.contains(search),
                Employee.position.contains(search),
                Employee.cc_name.contains(search)
            )
        )
    
    employees = query.order_by(Employee.emp_id).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/employees.html', 
                         employees=employees, 
                         search=search)

@admin_bp.route('/statistics')
@login_required
def statistics():
    """View registration statistics"""
    active_meeting = Meeting.get_active_meeting()
    
    if not active_meeting:
        flash('ไม่มีการประชุมที่เปิดอยู่', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    # Statistics by department
    dept_stats = db.session.query(
        Registration.sec_short,
        func.count(Registration.id).label('count')
    ).filter_by(
        meeting_id=active_meeting.id
    ).group_by(Registration.sec_short).order_by(desc('count')).all()
    
    # Statistics by hour
    hourly_stats = db.session.query(
        func.date_trunc('hour', Registration.registration_time).label('hour'),
        func.count(Registration.id).label('count')
    ).filter_by(
        meeting_id=active_meeting.id
    ).group_by('hour').order_by('hour').all()
    
    # Manual vs automatic registration
    manual_stats = db.session.query(
        Registration.is_manual_entry,
        func.count(Registration.id).label('count')
    ).filter_by(
        meeting_id=active_meeting.id
    ).group_by(Registration.is_manual_entry).all()
    
    return render_template('admin/statistics.html',
                         meeting=active_meeting,
                         dept_stats=dept_stats,
                         hourly_stats=hourly_stats,
                         manual_stats=manual_stats)

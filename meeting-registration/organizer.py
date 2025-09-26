# organizer.py - สร้างไฟล์ใหม่
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Meeting, Registration, User
from functools import wraps
from datetime import datetime

organizer_bp = Blueprint('organizer', __name__, url_prefix='/organizer')

def organizer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('กรุณาเข้าสู่ระบบ', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@organizer_bp.route('/')
@organizer_required
def dashboard():
    """Organizer dashboard"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Get user's meetings
    meetings = Meeting.query.filter_by(organizer_id=user_id).order_by(
        Meeting.created_at.desc()
    ).all()
    
    return render_template('organizer/dashboard.html', 
                         user=user, 
                         meetings=meetings)

@organizer_bp.route('/meeting/create', methods=['GET', 'POST'])
@organizer_required
def create_meeting():
    """Create new meeting"""
    if request.method == 'POST':
        user_id = session.get('user_id')
        
        meeting = Meeting(
            topic=request.form.get('topic'),
            meeting_date=datetime.strptime(request.form.get('meeting_date'), '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
            room=request.form.get('room'),
            floor=request.form.get('floor'),
            building=request.form.get('building'),
            organizer_id=user_id,
            is_active=True,
            is_public=request.form.get('is_public') == 'on'
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        flash('สร้างการประชุมสำเร็จ', 'success')
        return redirect(url_for('organizer.dashboard'))
    
    return render_template('organizer/create_meeting.html')

# organizer.py - เพิ่ม methods ที่ขาด

@organizer_bp.route('/meeting/<int:meeting_id>/edit', methods=['GET', 'POST'])
@organizer_required
def edit_meeting(meeting_id):
    """Edit meeting (only owner)"""
    user_id = session.get('user_id')
    meeting = Meeting.query.filter_by(id=meeting_id, organizer_id=user_id).first_or_404()
    
    if request.method == 'POST':
        meeting.topic = request.form.get('topic')
        meeting.meeting_date = datetime.strptime(request.form.get('meeting_date'), '%Y-%m-%d').date()
        meeting.start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        meeting.end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        meeting.room = request.form.get('room')
        meeting.floor = request.form.get('floor')
        meeting.building = request.form.get('building')
        meeting.is_public = request.form.get('is_public') == 'on'
        meeting.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('แก้ไขการประชุมสำเร็จ', 'success')
        return redirect(url_for('organizer.dashboard'))
    
    return render_template('organizer/edit_meeting.html', meeting=meeting)

@organizer_bp.route('/meeting/<int:meeting_id>/registrations')
@organizer_required
def view_registrations(meeting_id):
    """View registrations for organizer's meeting"""
    user_id = session.get('user_id')
    meeting = Meeting.query.filter_by(id=meeting_id, organizer_id=user_id).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    registrations = Registration.query.filter_by(
        meeting_id=meeting_id
    ).order_by(Registration.registration_time.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('organizer/registrations.html', 
                         meeting=meeting, 
                         registrations=registrations)

@organizer_bp.route('/meeting/<int:meeting_id>/export')
@organizer_required
def export_registrations(meeting_id):
    """Export registrations to CSV"""
    import csv
    import io
    from flask import send_file
    
    user_id = session.get('user_id')
    meeting = Meeting.query.filter_by(id=meeting_id, organizer_id=user_id).first_or_404()
    registrations = Registration.query.filter_by(meeting_id=meeting_id).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ลำดับ', 'รหัสพนักงาน', 'ชื่อ', 'ตำแหน่ง', 'หน่วยงาน', 'เวลาลงทะเบียน'])
    
    for idx, reg in enumerate(registrations, 1):
        writer.writerow([
            idx, reg.emp_id or '', reg.emp_name,
            reg.position or '', reg.sec_short or '',
            reg.registration_time.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    output_bytes = io.BytesIO()
    output_bytes.write(output.getvalue().encode('utf-8-sig'))
    output_bytes.seek(0)
    
    return send_file(
        output_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"registrations_{meeting_id}.csv"
    )
# organizer.py - ปรับปรุงใหม่
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
        
        # เพิ่ม current_user ใน kwargs
        kwargs['current_user'] = User.query.get(session['user_id'])
        return f(*args, **kwargs)
    return decorated_function

@organizer_bp.route('/')
@organizer_required
def dashboard(current_user):
    """Organizer dashboard"""
    # Get user's meetings
    meetings = Meeting.query.filter_by(organizer_id=current_user.id).order_by(
        Meeting.created_at.desc()
    ).all()
    
    return render_template('organizer/dashboard.html', 
                         user=current_user,
                         current_user=current_user,
                         meetings=meetings)

@organizer_bp.route('/meeting/create', methods=['GET', 'POST'])
@organizer_required
def create_meeting(current_user):
    """Create new meeting"""
    if request.method == 'POST':
        meeting = Meeting(
            topic=request.form.get('topic'),
            meeting_date=datetime.strptime(request.form.get('meeting_date'), '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
            room=request.form.get('room'),
            floor=request.form.get('floor'),
            building=request.form.get('building'),
            # เพิ่ม fields ใหม่
            meeting_type=request.form.get('meeting_type', 'onsite'),
            meeting_url=request.form.get('meeting_url'),
            meeting_id=request.form.get('meeting_id'),
            meeting_password=request.form.get('meeting_password'),
            additional_info=request.form.get('additional_info'),
            organizer_id=current_user.id,
            is_active=True,
            is_public=request.form.get('is_public') == 'on'
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        flash('สร้างการประชุมสำเร็จ', 'success')
        return redirect(url_for('organizer.dashboard'))
    
    return render_template('organizer/create_meeting.html', current_user=current_user)

@organizer_bp.route('/meeting/<int:meeting_id>/edit', methods=['GET', 'POST'])
@organizer_required
def edit_meeting(meeting_id, current_user):
    """Edit meeting (only owner)"""
    meeting = Meeting.query.filter_by(id=meeting_id, organizer_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        meeting.topic = request.form.get('topic')
        meeting.meeting_date = datetime.strptime(request.form.get('meeting_date'), '%Y-%m-%d').date()
        meeting.start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        meeting.end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        meeting.room = request.form.get('room')
        meeting.floor = request.form.get('floor')
        meeting.building = request.form.get('building')
        # เพิ่ม fields ใหม่
        meeting.meeting_type = request.form.get('meeting_type', 'onsite')
        meeting.meeting_url = request.form.get('meeting_url')
        meeting.meeting_id = request.form.get('meeting_id')
        meeting.meeting_password = request.form.get('meeting_password')
        meeting.additional_info = request.form.get('additional_info')
        meeting.is_public = request.form.get('is_public') == 'on'
        meeting.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('แก้ไขการประชุมสำเร็จ', 'success')
        return redirect(url_for('organizer.dashboard'))
    
    return render_template('organizer/edit_meeting.html', 
                         meeting=meeting, 
                         current_user=current_user)

@organizer_bp.route('/meeting/<int:meeting_id>/registrations')
@organizer_required
def view_registrations(meeting_id, current_user):
    """View registrations for organizer's meeting"""
    meeting = Meeting.query.filter_by(id=meeting_id, organizer_id=current_user.id).first_or_404()
    
    # ดึงข้อมูลผู้ลงทะเบียนทั้งหมด (ไม่ใช้ pagination ก่อน)
    registrations = Registration.query.filter_by(
        meeting_id=meeting_id
    ).order_by(Registration.registration_time.desc()).all()
    
    return render_template('organizer/registrations.html', 
                         meeting=meeting, 
                         registrations=registrations,
                         current_user=current_user)

@organizer_bp.route('/meeting/<int:meeting_id>/export/<format>')
@organizer_required
def export_registrations(meeting_id, format, current_user):
    """Export registrations to CSV or Excel"""
    import csv
    import io
    from flask import send_file
    
    meeting = Meeting.query.filter_by(id=meeting_id, organizer_id=current_user.id).first_or_404()
    registrations = Registration.query.filter_by(meeting_id=meeting_id).all()
    
    if format == 'csv':
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ลำดับ', 'รหัสพนักงาน', 'ชื่อ', 'ตำแหน่ง', 'หน่วยงาน', 'ศูนย์ต้นทุน', 'เวลาลงทะเบียน', 'ลงทะเบียนด้วยตนเอง'])
        
        for idx, reg in enumerate(registrations, 1):
            writer.writerow([
                idx, 
                reg.emp_id or '', 
                reg.emp_name,
                reg.position or '', 
                reg.sec_short or '',
                reg.cc_name or '',
                reg.registration_time.strftime('%Y-%m-%d %H:%M:%S'),
                'ใช่' if reg.is_manual_entry else 'ไม่'
            ])
        
        output.seek(0)
        output_bytes = io.BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return send_file(
            output_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"registrations_{meeting.topic}_{meeting.meeting_date}.csv"
        )
    
    elif format == 'excel':
        # Create Excel using pandas
        import pandas as pd
        
        data = []
        for idx, reg in enumerate(registrations, 1):
            data.append({
                'ลำดับ': idx,
                'รหัสพนักงาน': reg.emp_id or '',
                'ชื่อ-สกุล': reg.emp_name,
                'ตำแหน่ง': reg.position or '',
                'ส่วนงาน': reg.sec_short or '',
                'ศูนย์ต้นทุน': reg.cc_name or '',
                'เวลาลงทะเบียน': reg.registration_time.strftime('%Y-%m-%d %H:%M:%S'),
                'ลงทะเบียนด้วยตนเอง': 'ใช่' if reg.is_manual_entry else 'ไม่'
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='รายชื่อผู้ลงทะเบียน')
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"registrations_{meeting.topic}_{meeting.meeting_date}.xlsx"
        )
    
    flash('รูปแบบไฟล์ไม่ถูกต้อง', 'error')
    return redirect(url_for('organizer.view_registrations', meeting_id=meeting_id))
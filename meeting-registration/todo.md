สำหรับการทำ optimize ด้วย eager loading ต้องแก้ใน **app.py** ที่ฟังก์ชัน `index()` และ `register_meeting()`:

## 1. Import joinedload
```python
# เพิ่มที่ด้านบนของ app.py
from sqlalchemy.orm import joinedload
```

## 2. แก้ไขฟังก์ชัน index()
```python
@app.route('/')
def index():
    """Main registration page - แสดงตามจำนวนการประชุมที่ active"""
    
    # เปลี่ยนจากเดิม
    # active_meetings = Meeting.query.filter_by(
    #     is_active=True,
    #     is_public=True
    # ).all()
    
    # เป็นแบบ eager loading
    active_meetings = Meeting.query.options(
        joinedload(Meeting.organizer)
    ).filter_by(
        is_active=True,
        is_public=True
    ).all()
    
    # ... rest of code unchanged ...
```

## 3. แก้ไขฟังก์ชัน register_meeting()
```python
@app.route('/submit/<int:meeting_id>')
def register_meeting(meeting_id):
    """Registration page for specific meeting"""
    
    # เปลี่ยนจากเดิม
    # meeting = Meeting.query.get_or_404(meeting_id)
    
    # เป็นแบบ eager loading
    meeting = Meeting.query.options(
        joinedload(Meeting.organizer)
    ).filter(Meeting.id == meeting_id).first_or_404()
    
    if not meeting.is_active:
        flash('การประชุมนี้ปิดรับลงทะเบียนแล้ว', 'warning')
        return redirect(url_for('index'))
    
    return render_template('index.html', meeting=meeting)
```

## 4. (Optional) แก้ฟังก์ชัน register() และ register_manual()
ถ้าต้องการให้สมบูรณ์:
```python
# ในฟังก์ชัน register() - บรรทัดที่หา meeting
if meeting_id:
    meeting = Meeting.query.options(
        joinedload(Meeting.organizer)
    ).filter(Meeting.id == meeting_id).first_or_404()
else:
    # สำหรับ get_active_meeting() อาจต้องแก้ใน models.py
    meeting = Meeting.get_active_meeting()
```

## 5. (Optional) แก้ get_active_meeting() ใน models.py
```python
@classmethod
@cache.cached(timeout=60, key_prefix='active_meeting')
def get_active_meeting(cls):
    """Get the currently active meeting (cached for 60 seconds)"""
    max_retries = current_app.config.get('DATABASE_RETRY_COUNT', 3)
    retry_delay = current_app.config.get('DATABASE_RETRY_DELAY', 1)

    for attempt in range(max_retries):
        try:
            logger.debug(f"Fetching active meeting from DB (attempt {attempt + 1})")
            
            # เพิ่ม eager loading
            from sqlalchemy.orm import joinedload
            result = cls.query.options(
                joinedload(cls.organizer)
            ).filter_by(is_active=True).order_by(cls.created_at.desc()).first()
            
            return result
        except OperationalError as e:
            # ... error handling code unchanged ...
```

## ผลลัพธ์:
- **ก่อน optimize**: Query 2 ครั้ง (1 สำหรับ meeting, 1 สำหรับ organizer เมื่อเรียกใช้)
- **หลัง optimize**: Query 1 ครั้งเดียว (JOIN ทันที)

## ตรวจสอบผลลัพธ์:
เปิด SQL logging เพื่อดู queries:
```python
# ใน config.py
SQLALCHEMY_ECHO = True  # จะแสดง SQL queries ใน console
```

สำหรับระบบขนาดเล็กที่มี meeting ไม่เยอะ การ optimize นี้อาจไม่เห็นความแตกต่างมากนัก แต่เป็น best practice ที่ดีสำหรับระบบที่โตขึ้นในอนาคต
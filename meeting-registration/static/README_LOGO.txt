# การจัดการ Logo สำหรับ QR Code

## โครงสร้างไฟล์ที่ต้องการ
```
meeting-registration/
├── app.py
├── static/
│   └── logo.png         # วางไฟล์โลโก้ที่นี่
├── templates/
└── qrcode_utils.py
```

## วิธีการเพิ่มโลโก้

### Option 1: ใช้ชื่อไฟล์มาตรฐาน (แนะนำ)
1. คัดลอกไฟล์โลโก้ของคุณมาที่ `static/logo.png`
```bash
cp /path/to/your/logo.png static/logo.png
```

### Option 2: ใช้ชื่อไฟล์ 01_NT-Logo.png
1. คัดลอกไฟล์มาที่ static folder
```bash
cp 01_NT-Logo.png static/01_NT-Logo.png
```

### Option 3: ใช้ชื่อไฟล์อื่น
1. วางไฟล์ใน static folder
2. แก้ไข function `get_logo_path()` ใน app.py:
```python
def get_logo_path():
    """Get logo path relative to Flask app"""
    static_folder = app.static_folder or 'static'
    
    possible_logos = [
        'logo.png',
        '01_NT-Logo.png',
        'nt-logo.png',
        'your-custom-logo.png'  # เพิ่มชื่อไฟล์ของคุณที่นี่
    ]
    
    for filename in possible_logos:
        path = os.path.join(static_folder, filename)
        if os.path.exists(path):
            return path
    return None
```

## รูปแบบไฟล์ที่รองรับ
- **PNG** (แนะนำ) - รองรับ transparency
- **JPG/JPEG** - ไม่รองรับ transparency
- **ขนาดที่แนะนำ:** 200x200 - 500x500 pixels
- **พื้นหลัง:** โปร่งใส (transparent) จะดูดีที่สุด

## การทำงานของระบบ

### 1. ลำดับการค้นหาโลโก้
ระบบจะค้นหาไฟล์โลโก้ตามลำดับนี้:
1. `static/logo.png`
2. `static/01_NT-Logo.png`
3. `static/nt-logo.png`

### 2. กรณีไม่พบโลโก้
- ระบบจะสร้าง QR Code แบบไม่มีโลโก้
- ไม่มี error แต่จะมี warning ใน log

### 3. การแสดงผล
- โลโก้จะถูกวางตรงกลาง QR Code
- ขนาดโลโก้ = 1/5 ของขนาด QR Code
- มีพื้นหลังสีขาวรอบโลโก้เพื่อให้สแกนได้ง่าย

## ตรวจสอบการทำงาน

### 1. ทดสอบว่าพบโลโก้หรือไม่
```bash
cd meeting-registration
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from flask import Flask
    app = Flask(__name__)
    
    def get_logo_path():
        static_folder = app.static_folder or 'static'
        possible_logos = ['logo.png', '01_NT-Logo.png', 'nt-logo.png']
        for filename in possible_logos:
            path = os.path.join(static_folder, filename)
            if os.path.exists(path):
                return path
        return None
    
    logo = get_logo_path()
    if logo:
        print(f'✓ Logo found: {logo}')
    else:
        print('✗ No logo found')
"
```

### 2. ตรวจสอบไฟล์ใน static folder
```bash
ls -la static/
```

### 3. ดู log เมื่อสร้าง QR Code
```
INFO:qrcode_utils:Generating QR Code - with_logo: True, logo_path: static/logo.png
INFO:qrcode_utils:Logo file found at: static/logo.png
INFO:qrcode_utils:Logo added successfully to QR Code
```

## Troubleshooting

### ปัญหา: ไม่พบโลโก้
```
WARNING:qrcode_utils:No logo found. Tried paths: ['static/logo.png', 'static/01_NT-Logo.png', ...]
```
**วิธีแก้:** ตรวจสอบว่ามีไฟล์ใน static folder

### ปัญหา: โลโก้ไม่แสดงใน QR Code
**ตรวจสอบ:**
1. ไฟล์มีนามสกุลถูกต้อง (.png, .jpg)
2. ไฟล์ไม่เสียหาย
3. ขนาดไฟล์ไม่ใหญ่เกินไป (< 5MB)

### ปัญหา: QR Code สแกนไม่ได้
**วิธีแก้:** 
- ลดขนาดโลโก้ลง
- ใช้โลโก้ที่มีความคมชัดสูง
- ตรวจสอบว่า Error Correction Level = QUARTILE

## การ Deploy บน Production

### 1. ตรวจสอบไฟล์ก่อน deploy
```bash
# ตรวจสอบว่ามีโลโก้
test -f static/logo.png && echo "✓ Logo exists" || echo "✗ Logo missing"
```

### 2. Permission บน Linux Server
```bash
# ให้สิทธิ์อ่านไฟล์
chmod 644 static/logo.png
chmod 755 static/
```

### 3. Environment Variables
```bash
# .env file
APPLICATION_ROOT=/register  # ถ้ามี URL prefix
PREFERRED_URL_SCHEME=https  # สำหรับ production
```

## Best Practices

1. **ใช้ PNG format** - รองรับ transparency ทำให้ดูสวยงาม
2. **ขนาดไฟล์เล็ก** - ใช้ไฟล์ขนาดเล็ก (< 500KB) เพื่อความเร็ว
3. **โลโก้เรียบง่าย** - ใช้โลโก้ที่ไม่ซับซ้อนเกินไป เพื่อให้ QR Code สแกนได้ง่าย
4. **ทดสอบการสแกน** - ทดสอบสแกน QR Code ด้วยมือถือหลายรุ่น

## Notes
- ระบบใช้ relative path จึงทำงานได้ทั้ง local และ server
- ไม่ต้องแก้โค้ดเมื่อ deploy
- รองรับการทำงานกับ URL prefix (เช่น /register)
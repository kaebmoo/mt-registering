# ระบบลงทะเบียนการประชุม (Meeting Registration System)

ระบบลงทะเบียนการประชุมที่พัฒนาด้วย Flask และ PostgreSQL แทนระบบ PHP เดิม เพื่อเพิ่มประสิทธิภาพและป้องกันการลงทะเบียนซ้ำ พร้อมระบบ Multi-role Authentication สำหรับ Admin และ Organizers

## 🌟 คุณสมบัติหลัก

### สำหรับผู้ลงทะเบียน
- ✅ ลงทะเบียนด้วยรหัสพนักงาน พร้อมระบบค้นหาอัตโนมัติ
- ✅ รองรับการลงทะเบียนหลายการประชุมพร้อมกัน
- ✅ ป้องกันการลงทะเบียนซ้ำด้วย Database Constraint
- ✅ รองรับการกรอกข้อมูลด้วยตนเองกรณีไม่พบในระบบ
- ✅ แสดงสถานะการลงทะเบียนทันที
- ✅ **ระบบจัดเรียงการประชุมตามสถานะ**: กำลังดำเนินการ, วันนี้, กำลังจะมาถึง
- ✅ **QR Code สำหรับลงทะเบียน**: สแกน QR เพื่อลงทะเบียนได้ทันที
- ✅ **รองรับการประชุมออนไลน์**: แสดงลิงค์และข้อมูลการเข้าร่วมออนไลน์

### สำหรับผู้จัดการประชุม (Organizers)
- ✅ ระบบ Email OTP Authentication
- ✅ สร้างและจัดการการประชุมของตนเอง
- ✅ ดูรายชื่อผู้ลงทะเบียนในการประชุมที่จัด
- ✅ Export ข้อมูลเป็น CSV
- ✅ กำหนดการประชุมเป็น Public/Private
- ✅ **สร้าง QR Code สำหรับการประชุม**: ดาวน์โหลดและพิมพ์ QR Code
- ✅ **รองรับการประชุมแบบต่างๆ**: ณ สถานที่, ออนไลน์, และผสมผสาน (Hybrid)
- ✅ **จัดการข้อมูลการประชุมออนไลน์**: Meeting URL, ID, Password
- ✅ **แสดงสถิติการลงทะเบียน**: จำนวนผู้ลงทะเบียนปัจจุบัน

### สำหรับผู้ดูแลระบบ (Admin)
- ✅ Admin Dashboard สำหรับจัดการและดูสถิติ
- ✅ จัดการการประชุมทั้งหมดในระบบ
- ✅ ดูสถิติการลงทะเบียนแบบ Real-time
- ✅ จัดการข้อมูลพนักงาน
- ✅ ลบการลงทะเบียนแบบเดี่ยวหรือหลายรายการ

### ระบบสนับสนุน
- ✅ Rate Limiting ป้องกันการส่งฟอร์มซ้ำเร็วเกินไป
- ✅ ระบบแคชข้อมูลพนักงานด้วย Redis
- ✅ ส่งข้อมูลไป Google Sheets อัตโนมัติผ่าน Celery
- ✅ ส่ง Email OTP ผ่าน RQ Worker
- ✅ รองรับ Timezone (Asia/Bangkok)
- ✅ **QR Code Generator**: สร้าง QR Code พร้อมโลโก้องค์กร
- ✅ **Auto-refresh**: อัพเดตสถานะการประชุมอัตโนมัติทุก 5 นาที
- ✅ **Multi-tenant Support**: รองรับการแยกองค์กรแบบ SaaS (โฟลเดอร์ saas)

## 📊 การปรับปรุงจากระบบเดิม

1. **Performance**: ใช้ PostgreSQL แทนการอ่านไฟล์ CSV ทำให้เร็วขึ้นมาก
2. **Reliability**: ป้องกันการลงทะเบียนซ้ำด้วย Database Constraint
3. **Scalability**: รองรับผู้ใช้งานพร้อมกันจำนวนมาก
4. **Security**: มีระบบ Rate Limiting, Session Management และ Email OTP
5. **Management**: มี Admin Dashboard และ Organizer Dashboard
6. **Multi-tenancy**: รองรับการจัดการประชุมหลายงานโดยผู้จัดต่างคน

## 🔧 Requirements

### Core Requirements
- Python 3.11+
- PostgreSQL 15+
- Redis (สำหรับ Cache และ Queue)

### QR Code Requirements (**ใหม่**)
- PIL/Pillow (สำหรับ image processing)
- qrcodegen (สำหรับสร้าง QR Code)
- Logo files: `logo.png`, `01_NT-Logo.png` (วางใน folder `static/`)

### Optional (for production)
- Nginx (Reverse Proxy)
- PM2 (Process Manager)
- Docker & Docker Compose

## 📁 โครงสร้างไฟล์

```
meeting-registration/
├── app.py                 # Main Flask application พร้อม factory pattern
├── models.py             # Database models (Employee, User, Meeting, Registration, OTPToken)
├── config.py             # Configuration classes สำหรับ environments ต่างๆ
├── requirements.txt      # Python dependencies
├── database_schema.sql   # PostgreSQL schema พร้อม tables ทั้งหมด
├── README.md            # Documentation
├── import_data.py       # Script สำหรับ import ข้อมูล
├── extensions.py        # Flask extensions (cache, celery)
│
├── 📧 Email & Background Tasks
│   ├── email_service.py      # Email service class สำหรับส่ง OTP
│   ├── tasks.py              # Background tasks definitions (RQ)
│   ├── celery_worker.py      # Celery worker for Google Sheets
│   └── rq_worker.py          # RQ worker for email OTP
│
├── 🔐 Authentication & Authorization
│   ├── auth.py               # Authentication blueprint (login/register with OTP)
│   ├── admin.py              # Admin blueprint และ dashboard
│   └── organizer.py          # Organizer blueprint สำหรับผู้จัดการประชุม
│
├── 🛠️ Utilities
│   ├── timezone_utils.py     # Timezone conversion helpers
│   ├── meeting_utils.py      # Meeting-related utility functions
│   └── qrcode_utils.py       # QR Code generation with logo support
│
├── 🐳 Deployment & Configuration
│   ├── docker-compose.yml    # Docker compose configuration
│   ├── Dockerfile           # Docker image definition
│   ├── ecosystem.config.js   # PM2 configuration (3 processes)
│   ├── .env.example         # Environment variables template
│   ├── env.development      # Development environment config
│   └── env.production       # Production environment config
│
├── 📂 templates/             # Jinja2 HTML templates
│   ├── base.html            # Base template พร้อม navigation
│   ├── index.html           # หน้าลงทะเบียน (single meeting)
│   ├── index_multi.html     # หน้าเลือกการประชุม (multiple meetings พร้อมจัดกลุ่มตามสถานะ)
│   ├── manual_registration.html  # ฟอร์มกรอกข้อมูลเอง
│   ├── registration_success.html # หน้าแสดงผลสำเร็จ
│   ├── qrcode_display.html  # **ใหม่**: หน้าแสดง QR Code สำหรับการประชุม
│   ├── 404.html            # Error page - Not Found
│   ├── 500.html            # Error page - Server Error
│   │
│   ├── 📁 partials/         # **ใหม่**: Template components
│   │   └── meeting_card.html    # Card component สำหรับแสดงการประชุม
│   │
│   ├── 📁 admin/           # Admin templates
│   │   ├── admin_base.html     # Base template สำหรับ admin
│   │   ├── login.html          # Admin login page
│   │   ├── dashboard.html      # Admin dashboard พร้อมสถิติ
│   │   ├── meetings.html       # จัดการการประชุมทั้งหมด
│   │   ├── create_meeting.html # สร้างการประชุมใหม่
│   │   ├── edit_meeting.html   # แก้ไขการประชุม
│   │   ├── registrations.html  # รายชื่อผู้ลงทะเบียน
│   │   ├── employees.html      # จัดการข้อมูลพนักงาน
│   │   ├── statistics.html     # สถิติการลงทะเบียน
│   │   └── components/
│   │       └── pagination.html # Reusable pagination component
│   │
│   ├── 📁 auth/            # Authentication templates
│   │   ├── login.html          # เข้าสู่ระบบด้วย email
│   │   ├── register.html       # ลงทะเบียนผู้จัด
│   │   └── verify_otp.html     # ยืนยัน OTP code
│   │
│   └── 📁 organizer/       # Organizer templates
│       ├── dashboard.html      # Organizer dashboard
│       ├── create_meeting.html # สร้างการประชุม
│       ├── edit_meeting.html   # แก้ไขการประชุมของตนเอง
│       └── registrations.html  # ดูผู้ลงทะเบียนในงานของตน
│
├── 📂 static/              # Static assets (ถ้ามี)
│   ├── css/
│   ├── js/
│   └── images/
│
├── 📂 logs/               # Application logs
│   ├── app.log
│   ├── pm2-error.log
│   ├── pm2-out.log
│   ├── pm2-combined.log
│   ├── pm2-celery-error.log
│   ├── pm2-celery-out.log
│   └── pm2-rq-error.log
│
└── 📂 saas/               # **ใหม่**: Multi-tenant SaaS version กำลังพัฒนา ไม่ว่างจริงทำไม่ได้ ;-) 
    ├── app.py             # SaaS version ของแอพ
    ├── models/            # SaaS database models พร้อม multi-tenancy
    ├── templates/         # SaaS-specific templates
    └── requirements.txt   # SaaS version dependencies
```

## 🚀 การติดตั้ง

### วิธีที่ 1: การติดตั้งแบบ Docker (แนะนำ)

```bash
# Clone repository
git clone <repository-url>
cd meeting-registration

# สร้างไฟล์ .env
cp .env.example .env
# แก้ไข .env ตามต้องการ

# Build and run
docker-compose up -d

# Import data
docker-compose exec web python import_data.py --employees employee.csv

# Access application at http://localhost:5000
```

### วิธีที่ 2: การติดตั้งแบบ Manual

#### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Setup PostgreSQL

```bash
# วิธีที่ 1: ใช้ createdb (ถ้ามี)
createdb -U postgres meeting_registration

# วิธีที่ 2: ใช้ psql
psql -U postgres -c "CREATE DATABASE meeting_registration"

# วิธีที่ 3: ใช้ sudo (Linux)
sudo -u postgres createdb meeting_registration

# รัน schema
psql -d meeting_registration -f database_schema.sql
```

#### 3. Setup Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# macOS
brew install redis
brew services start redis
```

#### 4. Setup environment variables

```bash
# Development
cp env.development .env

# Production
cp env.production .env

# แก้ไขค่าใน .env ตามต้องการ
```

#### 5. Run migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### 6. Import ข้อมูล

```bash
python import_data.py --employees employee.csv
python import_data.py --meeting schedule.json
```

#### 7. **อัพเดต Database Schema** (สำหรับการประชุมออนไลน์)

```sql
-- เพิ่ม fields ใหม่สำหรับรองรับการประชุมออนไลน์
ALTER TABLE meetings ADD COLUMN meeting_type VARCHAR(50) DEFAULT 'onsite';
ALTER TABLE meetings ADD COLUMN meeting_url TEXT;
ALTER TABLE meetings ADD COLUMN meeting_id VARCHAR(100);
ALTER TABLE meetings ADD COLUMN meeting_password VARCHAR(100);
ALTER TABLE meetings ADD COLUMN additional_info TEXT;
```

#### 8. Run application

```bash
# Development
python app.py

# Production with Gunicorn
gunicorn --bind 0.0.0.0:9000 --workers 4 --timeout 120 "app:create_app()"
```

## 🚀 Deployment with PM2

### สร้างไฟล์ ecosystem.config.js

```javascript
module.exports = {
  apps: [{
    // Process 1: Main Application
    name: 'meeting-registration',
    script: '/home/seal/.local/bin/gunicorn',
    args: '--bind 0.0.0.0:9000 --workers 4 --timeout 120 "app:create_app()"',
    cwd: '/home/seal/mt-registering/meeting-registration',
    interpreter: 'none',
    env: {
      FLASK_ENV: 'production',
      PORT: 9000
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true,
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  },
  {
    // Process 2: Celery Worker (สำหรับ Google Sheets)
    name: 'meeting-celery-worker',
    script: '/home/seal/.local/bin/celery',
    args: '-A celery_worker.celery_app worker --loglevel=info',
    cwd: '/home/seal/mt-registering/meeting-registration',
    interpreter: 'none',
    env: {
      FLASK_ENV: 'production'
    },
    error_file: './logs/pm2-celery-error.log',
    out_file: './logs/pm2-celery-out.log',
    log_file: './logs/pm2-celery-combined.log',
    time: true,
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M'
  },
  {
    // Process 3: RQ Worker (สำหรับ Email OTP)
    name: 'meeting-rq-worker',
    script: '/home/seal/.local/bin/python',
    args: 'rq_worker.py',
    cwd: '/home/seal/mt-registering/meeting-registration',
    interpreter: 'none',
    env: {
      FLASK_ENV: 'production',
      REDIS_URL: 'redis://localhost:6379'
    },
    error_file: './logs/pm2-rq-error.log',
    out_file: './logs/pm2-rq-out.log',
    log_file: './logs/pm2-rq-combined.log',
    time: true,
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M'
  }]
};
```

### PM2 Commands

```bash
# Start all processes
pm2 start ecosystem.config.js

# Alternative: Start individually
pm2 start gunicorn \
  --name "meeting-registration" \
  --interpreter none \
  -- --bind 0.0.0.0:9000 \
  --workers 4 \
  --timeout 120 \
  --chdir /path/to/meeting-registration \
  "app:create_app('production')"

# List all processes
pm2 list

# Monitor
pm2 monit

# View logs
pm2 logs meeting-registration
pm2 logs meeting-registration --lines 100
pm2 logs meeting-celery-worker
pm2 logs meeting-rq-worker

# Restart
pm2 restart meeting-registration

# Reload (zero-downtime)
pm2 reload meeting-registration

# Stop
pm2 stop meeting-registration

# Delete from PM2
pm2 delete meeting-registration

# Save PM2 process list
pm2 save

# Setup startup script
pm2 startup

# Status
pm2 status meeting-registration

# Show details
pm2 describe meeting-registration

# Reset restart counter
pm2 reset meeting-registration
```

## 🌐 Nginx Configuration

```nginx
# เพิ่ม upstream สำหรับ Flask app
upstream flask_meeting_app {
    server localhost:9000;
    keepalive 64;
}

server {
    listen 443 ssl;
    server_name host.name.com;
    
    ssl_certificate_key /etc/letsencrypt/live/host.name.com/privkey.pem;
    ssl_certificate /etc/letsencrypt/live/host.name.com/fullchain.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Flask Meeting Registration App
    location /register/ {
        # Proxy to Flask app
        proxy_pass http://flask_meeting_app/;
        
        # Headers สำหรับ Flask app
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /register;
        
        # WebSocket support (ถ้าต้องการ)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 240s;
        
        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
        
        # Redirect handling
        proxy_redirect off;
    }

    # Admin panel
    location /register/admin/ {
        proxy_pass http://flask_meeting_app/admin/;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /register;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_read_timeout 240s;
    }

    # Static files (ถ้ามี)
    location /register/static/ {
        proxy_pass http://flask_meeting_app/static/;
        
        # Cache static files
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Other locations...
}
```

Reload Nginx:

```bash
# Test configuration
sudo nginx -t

# If OK, reload
sudo systemctl reload nginx
```

## 📝 การใช้งาน

### สำหรับผู้ลงทะเบียน

#### วิธีลงทะเบียนแบบปกติ
1. เข้าหน้าลงทะเบียน
2. เลือกการประชุม (ถ้ามีหลายงาน - ระบบจะจัดกลุ่มตามสถานะ)
3. กรอกรหัสพนักงาน (ไม่ต้องใส่ 0 นำหน้า)
4. ระบบจะค้นหาข้อมูลอัตโนมัติ
5. หากไม่พบ สามารถกรอกข้อมูลเองได้
6. กด "ลงทะเบียน"

#### วิธีลงทะเบียนด้วย QR Code (**ใหม่**)
1. สแกน QR Code ที่ได้รับจากผู้จัดการประชุม
2. เข้าสู่หน้าลงทะเบียนโดยอัตโนมัติ
3. กรอกรหัสพนักงานและลงทะเบียนตามปกติ

### สำหรับผู้จัดการประชุม (Organizers)

1. ลงทะเบียนเข้าใช้งานที่ `/auth/register`
2. ระบบจะส่ง OTP ไปยัง email
3. ยืนยัน OTP
4. เข้าสู่ระบบที่ `/auth/login`
5. จัดการการประชุม:
   - สร้างการประชุมใหม่ (รองรับ 3 รูปแบบ: ณ สถานที่, ออนไลน์, ผสมผสาน)
   - แก้ไขการประชุม พร้อมกำหนดข้อมูลออนไลน์
   - ดูรายชื่อผู้ลงทะเบียนพร้อมสถิติ
   - **สร้าง QR Code**: ดู, ดาวน์โหลด, และพิมพ์ QR Code
   - Export ข้อมูล CSV

### สำหรับ Admin

1. เข้าสู่ระบบที่ `/admin`
2. ใช้ username/password ที่ตั้งไว้ใน .env
3. จัดการระบบ:
   - จัดการการประชุมทั้งหมด
   - ดูสถิติการลงทะเบียน
   - จัดการข้อมูลพนักงาน
   - ลบการลงทะเบียน
   - Export ข้อมูล

## 🔍 API Endpoints

### Public Endpoints
- `GET /` - หน้าหลัก (แสดงการประชุมที่ active พร้อมจัดกลุ่มตามสถานะ)
- `GET /submit/<meeting_id>` - หน้าลงทะเบียนสำหรับการประชุมเฉพาะ
- `POST /submit` - ส่งข้อมูลลงทะเบียน
- `POST /submit/<meeting_id>` - ลงทะเบียนในการประชุมที่ระบุ
- `POST /submit_manual` - ลงทะเบียนแบบกรอกเอง
- `POST /submit_manual/<meeting_id>` - ลงทะเบียนแบบกรอกเองในการประชุมที่ระบุ
- `GET /api/check_employee/<emp_id>` - ตรวจสอบข้อมูลพนักงาน
- `GET /api/registration_status/<meeting_id>/<emp_id>` - ตรวจสอบสถานะการลงทะเบียน

### QR Code Endpoints (**ใหม่**)
- `GET /meeting/<meeting_id>/qrcode` - **แสดงหน้า QR Code สำหรับการประชุม**
- `GET /meeting/<meeting_id>/qrcode/download` - **ดาวน์โหลด QR Code เป็นไฟล์ PNG**

### Authentication Endpoints
- `GET /auth/register` - หน้าลงทะเบียนผู้จัดการ
- `POST /auth/register` - ส่งข้อมูลลงทะเบียน
- `GET /auth/verify-register` - หน้ายืนยัน OTP สำหรับลงทะเบียน
- `POST /auth/verify-register` - ยืนยัน OTP
- `GET /auth/login` - หน้าเข้าสู่ระบบ
- `POST /auth/login` - ส่งข้อมูลเข้าสู่ระบบ
- `GET /auth/verify-login` - หน้ายืนยัน OTP สำหรับ login
- `POST /auth/verify-login` - ยืนยัน OTP
- `GET /auth/logout` - ออกจากระบบ
- `GET /auth/check-email-status` - ตรวจสอบสถานะการส่ง email (AJAX)

### Organizer Endpoints
- `GET /organizer/` - Dashboard ผู้จัดการประชุม
- `GET /organizer/meeting/create` - สร้างการประชุม
- `POST /organizer/meeting/create` - บันทึกการประชุมใหม่
- `GET /organizer/meeting/<id>/edit` - แก้ไขการประชุม
- `POST /organizer/meeting/<id>/edit` - บันทึกการแก้ไข
- `GET /organizer/meeting/<id>/registrations` - ดูผู้ลงทะเบียน
- `GET /organizer/meeting/<id>/export` - Export CSV

### Admin Endpoints
- `GET /admin` - Admin dashboard
- `GET /admin/login` - หน้าเข้าสู่ระบบ admin
- `POST /admin/login` - ส่งข้อมูลเข้าสู่ระบบ
- `GET /admin/logout` - ออกจากระบบ
- `GET /admin/meetings` - จัดการการประชุม
- `GET /admin/meetings/create` - สร้างการประชุม
- `POST /admin/meetings/create` - บันทึกการประชุมใหม่
- `GET /admin/meetings/<id>/edit` - แก้ไขการประชุม
- `POST /admin/meetings/<id>/edit` - บันทึกการแก้ไข
- `POST /admin/meetings/<id>/delete` - ลบการประชุม
- `GET /admin/meetings/<id>/toggle` - เปิด/ปิดการประชุม
- `GET /admin/registrations/<meeting_id>` - ดูรายชื่อผู้ลงทะเบียน
- `GET /admin/registrations/<meeting_id>/export` - Export CSV
- `POST /admin/registrations/<id>/delete` - ลบการลงทะเบียนเดี่ยว
- `POST /admin/registrations/delete_multiple` - ลบหลายการลงทะเบียน
- `POST /admin/registrations/<meeting_id>/delete_all` - ลบทั้งหมด
- `GET /admin/employees` - จัดการข้อมูลพนักงาน
- `GET /admin/statistics` - ดูสถิติ

## 🐛 Troubleshooting

### ปัญหา: ลงทะเบียนไม่ได้
- ตรวจสอบว่ามีการประชุมที่ active อยู่
- ตรวจสอบ rate limit (รอ 5 วินาทีระหว่างการลงทะเบียน)
- ตรวจสอบว่าไม่ได้ลงทะเบียนซ้ำ

### ปัญหา: ไม่พบข้อมูลพนักงาน
- ตรวจสอบว่า import ข้อมูลแล้ว
- ลองค้นหาโดยไม่ใส่ 0 นำหน้า
- สามารถกรอกข้อมูลเองได้

### ปัญหา: Email OTP ไม่ส่ง
- ตรวจสอบ MAIL_* settings ใน .env
- ตรวจสอบว่า RQ worker ทำงาน: `pm2 logs meeting-rq-worker`
- ตรวจสอบ App-specific password สำหรับ Gmail

### ปัญหา: Admin เข้าไม่ได้
- ตรวจสอบ username/password ใน .env
- Default: admin/admin2024

### ปัญหา: Connection Pool Exhausted
- เพิ่มค่า pool_size ใน config.py
- ตรวจสอบ max_connections ใน PostgreSQL

## 📊 Database Operations

### ดู Logs
```bash
# PM2 logs
pm2 logs meeting-registration --lines 100

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Application logs
tail -f logs/app.log
```

### ดู Database
```bash
# เข้า PostgreSQL
psql -U postgres -d meeting_registration

# ดูจำนวนการลงทะเบียน
SELECT COUNT(*) FROM registrations WHERE meeting_id = 1;

# ดูการลงทะเบียนล่าสุด
SELECT emp_id, emp_name, registration_time 
FROM registrations 
ORDER BY registration_time DESC 
LIMIT 10;

# ดูสถิติตามแผนก
SELECT sec_short, COUNT(*) as count 
FROM registrations 
WHERE meeting_id = 1 
GROUP BY sec_short 
ORDER BY count DESC;

# ลบ OTP ที่หมดอายุ
DELETE FROM otp_tokens WHERE expires_at < CURRENT_TIMESTAMP;
```

## 🔐 Security Considerations

1. **Passwords**: เปลี่ยน SECRET_KEY และ passwords ทั้งหมดใน production
2. **HTTPS**: ใช้ HTTPS เสมอใน production
3. **Database**: จำกัด database permissions
4. **Firewall**: Setup firewall rules อย่างเหมาะสม
5. **Rate Limiting**: ปรับค่า rate limit ตามความเหมาะสม
6. **Email Domains**: กำหนด ALLOWED_EMAIL_DOMAINS เพื่อจำกัดการลงทะเบียน

## 💾 Backup & Recovery

### Backup Database
```bash
# Full backup
pg_dump -U postgres meeting_registration > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
pg_dump -U postgres -Fc meeting_registration > backup_$(date +%Y%m%d_%H%M%S).dump

# Backup specific tables
pg_dump -U postgres -t registrations -t meetings meeting_registration > registrations_backup.sql
```

### Restore Database
```bash
# From SQL file
psql -U postgres meeting_registration < backup.sql

# From compressed dump
pg_restore -U postgres -d meeting_registration backup.dump

# Restore specific table
psql -U postgres meeting_registration < registrations_backup.sql
```

### Automated Backup (crontab)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * pg_dump -U postgres meeting_registration | gzip > /backup/meeting_reg_$(date +\%Y\%m\%d).sql.gz

# Keep only last 7 days
0 3 * * * find /backup -name "meeting_reg_*.sql.gz" -mtime +7 -delete
```

## 🚀 Performance Tips

1. **Database Indexing**: ตรวจสอบว่ามี index ที่จำเป็น (ดู database_schema.sql)
2. **Redis Caching**: ใช้ Redis สำหรับ cache และ rate limiting
3. **Connection Pooling**: ปรับ pool_size ตามจำนวนการใช้งาน
4. **Gunicorn Workers**: ปรับจำนวน workers = (2 × CPU cores) + 1
5. **PostgreSQL Tuning**: ปรับ shared_buffers, work_mem ตามขนาด RAM
6. **Nginx Caching**: เปิด cache สำหรับ static files

## 🔌 SSH Tunnel (สำหรับ Remote Database)

```bash
# สร้าง SSH Tunnel
ssh -L [LOCAL_PORT]:[REMOTE_HOST]:[REMOTE_PORT] username@server.com -N

# ตัวอย่าง
ssh -L 5433:localhost:5432 username@centraldigital.cattelecom.com -N

# โดยที่:
# LOCAL_PORT = port ที่ local machine (ตรงกับ POSTGRES_PORT ใน .env)
# REMOTE_HOST = localhost หรือ 127.0.0.1 (database host บน server)
# REMOTE_PORT = port ที่ PostgreSQL ฟังอยู่บน server
```

## 🔑 Database Permissions

```sql
-- ดูว่ามี user อะไรบ้าง
\du

-- ดูว่าใช้ database อะไร
\l

-- เข้า database ที่ถูกต้อง
\c meeting_registration;

-- ดูว่ามีตารางอะไรบ้าง
\dt

-- Grant ALL privileges สำหรับทุกตารางที่มีอยู่
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;

-- Grant privileges สำหรับตารางที่จะสร้างในอนาคต
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO your_username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO your_username;

-- หรือถ้าต้องการ grant เฉพาะตารางที่จำเป็น
GRANT ALL PRIVILEGES ON TABLE employees TO your_username;
GRANT ALL PRIVILEGES ON TABLE meetings TO your_username;
GRANT ALL PRIVILEGES ON TABLE registrations TO your_username;
GRANT ALL PRIVILEGES ON TABLE users TO your_username;
GRANT ALL PRIVILEGES ON TABLE otp_tokens TO your_username;

-- Grant usage on sequences (สำหรับ auto-increment IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_username;
```

## Support & Contact

หากพบปัญหาหรือต้องการความช่วยเหลือ:
- Issues: https://github.com/kaebmoo/mt-registering/issues
- อยากได้อะไรเพิ่มหรือพูดคุย: https://github.com/kaebmoo/mt-registering/discussions 

## 🎯 คุณสมบัติใหม่ที่เพิ่มเข้ามา

### QR Code System
- **สร้าง QR Code**: สร้าง QR Code สำหรับแต่ละการประชุมพร้อมโลโก้องค์กร
- **ดาวน์โหลด**: ดาวน์โหลด QR Code เป็นไฟล์ PNG
- **พิมพ์**: รองรับการพิมพ์ QR Code โดยตรง
- **Logo Integration**: รองรับการใส่โลโก้ในกลาง QR Code

### รองรับการประชุมออนไลน์
- **3 รูปแบบการประชุม**: 
  - **ณ สถานที่** (Onsite): ระบุห้อง, ชั้น, อาคาร
  - **ออนไลน์** (Online): ระบุ Meeting URL, ID, Password
  - **ผสมผสาน** (Hybrid): รองรับทั้งสองรูปแบบ
- **แสดงข้อมูลออนไลน์**: แสดงลิงค์และข้อมูลการเข้าร่วมให้ผู้ลงทะเบียน

### การจัดเรียงการประชุมตามสถานะ
- **กำลังดำเนินการ**: การประชุมที่กำลังจัดอยู่ (มีไฟสีแดงกะพริบ)
- **วันนี้**: การประชุมที่จะเริ่มในวันนี้
- **กำลังจะมาถึง**: การประชุมในอนาคต
- **ผ่านไปแล้ว**: ประวัติการประชุม (แสดง 5 รายการล่าสุด)

### Multi-tenant SaaS Support
- **แยกองค์กร**: รองรับการแยกข้อมูลแต่ละองค์กรแบบ SaaS
- **ระบบ Tenant Context**: จัดการ context ของแต่ละองค์กร
- **เลือกองค์กร**: หน้าเลือกองค์กรสำหรับ multi-tenant mode

## Version History

- **v2.1.0** (Current) - QR Code System, Online Meeting Support, Smart Meeting Status
- **v2.0.0** - Multi-role authentication, Email OTP, Organizer system
- **v1.5.0** - Multiple meetings support
- **v1.0.0** - Initial Flask migration from PHP

## License

MIT License - See LICENSE file for details

## Credits

Developed by Managerial Accounting Department / kaebmoo
Based on original PHP system by thanyapat04

---
Last Updated: 2025
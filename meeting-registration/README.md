# ระบบลงทะเบียนการประชุม (Meeting Registration System)

ระบบลงทะเบียนการประชุมที่พัฒนาด้วย Flask และ PostgreSQL แทนระบบ PHP เดิม เพื่อเพิ่มประสิทธิภาพและป้องกันการลงทะเบียนซ้ำ

## คุณสมบัติหลัก

- ✅ ลงทะเบียนด้วยรหัสพนักงาน พร้อมระบบค้นหาอัตโนมัติ
- ✅ ป้องกันการลงทะเบียนซ้ำด้วย Database Constraint
- ✅ Rate Limiting ป้องกันการส่งฟอร์มซ้ำเร็วเกินไป
- ✅ ระบบแคชข้อมูลพนักงานด้วย Redis
- ✅ Admin Dashboard สำหรับจัดการและดูสถิติ
- ✅ Export ข้อมูลเป็น CSV
- ✅ ส่งข้อมูลไป Google Sheets อัตโนมัติ
- ✅ รองรับการกรอกข้อมูลด้วยตนเองกรณีไม่พบในระบบ

## การปรับปรุงจากระบบเดิม

1. **Performance**: ใช้ PostgreSQL แทนการอ่านไฟล์ CSV ทำให้เร็วขึ้นมาก
2. **Reliability**: ป้องกันการลงทะเบียนซ้ำด้วย Database Constraint
3. **Scalability**: รองรับผู้ใช้งานพร้อมกันจำนวนมาก
4. **Security**: มีระบบ Rate Limiting และ Session Management
5. **Management**: มี Admin Dashboard สำหรับจัดการ

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis (สำหรับ Rate Limiting)
- Docker & Docker Compose (optional)

## การติดตั้งแบบ Docker (แนะนำ)

1. Clone repository:
```bash
git clone <repository-url>
cd meeting-registration
```

2. สร้างไฟล์ `.env`:
```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=meeting_registration

# Application
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=production

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-admin-password

# Google Sheets Integration
GOOGLE_SCRIPT_URL=https://script.google.com/macros/s/YOUR-SCRIPT-ID/exec
```

3. รัน Docker Compose:
```bash
docker-compose up -d
```

4. Import ข้อมูลพนักงาน:
```bash
docker-compose exec web python import_data.py --employees employee.csv
```

5. Import ข้อมูลการประชุม:
```bash
docker-compose exec web python import_data.py --meeting schedule.json
```

6. เข้าใช้งาน:
- ระบบลงทะเบียน: http://localhost:5000
- Admin Dashboard: http://localhost:5000/admin

## การติดตั้งแบบ Manual

1. ติดตั้ง Dependencies:
```bash
pip install -r requirements.txt
```

2. Setup PostgreSQL:
```bash
# สร้าง database
createdb meeting_registration

# รัน schema
psql -d meeting_registration -f database_schema.sql
```

3. Setup environment variables:
```bash
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=yourpassword
export POSTGRES_DB=meeting_registration
export SECRET_KEY=your-secret-key
export FLASK_ENV=development
```

4. รัน migrations:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Import ข้อมูล:
```bash
python import_data.py --employees employee.csv
python import_data.py --meeting schedule.json
```

6. รัน application:
```bash
python app.py
```

## โครงสร้างไฟล์

```
meeting-registration/
├── app.py                 # Main Flask application
├── admin.py              # Admin blueprint
├── models.py             # Database models
├── config.py             # Configuration
├── import_data.py        # Data import script
├── requirements.txt      # Python dependencies
├── database_schema.sql   # PostgreSQL schema
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Docker image
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── manual_registration.html
│   ├── registration_success.html
│   └── admin/
│       ├── login.html
│       └── dashboard.html
└── README.md
```

## การใช้งาน

### สำหรับผู้ใช้ทั่วไป

1. เข้าหน้าลงทะเบียน
2. กรอกรหัสพนักงาน (ไม่ต้องใส่ 0 นำหน้า)
3. ระบบจะค้นหาข้อมูลอัตโนมัติ
4. หากไม่พบ สามารถกรอกข้อมูลเองได้
5. กด "ลงทะเบียน"

### สำหรับ Admin

1. เข้าสู่ระบบที่ `/admin`
2. จัดการการประชุม:
   - สร้างการประชุมใหม่
   - เปิด/ปิดการลงทะเบียน
   - ดูรายชื่อผู้ลงทะเบียน
   - Export ข้อมูลเป็น CSV
3. ดูสถิติการลงทะเบียน
4. จัดการข้อมูลพนักงาน

## API Endpoints

- `GET /` - หน้าลงทะเบียน
- `POST /register` - ส่งข้อมูลลงทะเบียน
- `POST /register_manual` - ลงทะเบียนแบบกรอกเอง
- `GET /api/check_employee/<emp_id>` - ตรวจสอบข้อมูลพนักงาน
- `GET /api/registration_status/<meeting_id>/<emp_id>` - ตรวจสอบสถานะการลงทะเบียน
- `GET /admin` - Admin dashboard
- `GET /admin/meetings` - จัดการการประชุม
- `GET /admin/registrations/<meeting_id>` - ดูรายชื่อผู้ลงทะเบียน
- `GET /admin/registrations/<meeting_id>/export` - Export CSV

## การ Monitoring

### ดู Logs
```bash
# Docker
docker-compose logs -f web

# Manual
tail -f logs/app.log
```

### ดู Database
```bash
# เข้า PostgreSQL
docker-compose exec postgres psql -U postgres -d meeting_registration

# ดูจำนวนการลงทะเบียน
SELECT COUNT(*) FROM registrations WHERE meeting_id = 1;

# ดูการลงทะเบียนล่าสุด
SELECT emp_id, emp_name, registration_time 
FROM registrations 
ORDER BY registration_time DESC 
LIMIT 10;
```

## Troubleshooting

### ปัญหา: ลงทะเบียนไม่ได้
- ตรวจสอบว่ามีการประชุมที่ active อยู่
- ตรวจสอบ rate limit (รอ 5 วินาทีระหว่างการลงทะเบียน)
- ตรวจสอบว่าไม่ได้ลงทะเบียนซ้ำ

### ปัญหา: ไม่พบข้อมูลพนักงาน
- ตรวจสอบว่า import ข้อมูลแล้ว
- ลองค้นหาโดยไม่ใส่ 0 นำหน้า
- สามารถกรอกข้อมูลเองได้

### ปัญหา: Admin เข้าไม่ได้
- ตรวจสอบ username/password ใน environment variables
- Default: admin/admin2024

## Performance Tips

1. **Database Indexing**: ตรวจสอบว่ามี index ที่จำเป็น
2. **Redis Caching**: ใช้ Redis สำหรับ rate limiting
3. **Connection Pooling**: PostgreSQL connection pool ถูกตั้งค่าอัตโนมัติ
4. **Gunicorn Workers**: ปรับจำนวน workers ตามจำนวน CPU cores

## Security Considerations

1. เปลี่ยน SECRET_KEY ใน production
2. ใช้ HTTPS ใน production
3. เปลี่ยน admin password default
4. จำกัด database permissions
5. Setup firewall rules

## Backup & Recovery

### Backup Database
```bash
# Backup
docker-compose exec postgres pg_dump -U postgres meeting_registration > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres meeting_registration < backup.sql
```

## License

MIT License

## Support

หากพบปัญหาหรือต้องการความช่วยเหลือ กรุณาติดต่อ IT Support

## SSH Tunnel

```ssh -L [LOCAL_PORT]:[REMOTE_HOST]:[REMOTE_PORT] username@centraldigital.cattelecom.com -N```

```
# โดยที่:
# LOCAL_PORT = port ที่ local machine (ตรงกับ POSTGRES_PORT ใน .env)
# REMOTE_HOST = localhost หรือ 127.0.0.1 (database host บน server)
# REMOTE_PORT = port ที่ PostgreSQL ฟังอยู่บน server
```

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

-- Grant usage on sequences (สำหรับ auto-increment IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_username;
```

คำสั่ง PM2 สำหรับรัน Flask App:

1. สร้างไฟล์ ecosystem.config.js:

```javascript 
module.exports = {
  apps: [
    {
      // --- Process 1: Flask/Gunicorn Web App (เหมือนเดิม) ---
      name: 'meeting-registration',
      script: '/usr/local/bin/gunicorn', // หรือ path ไปยัง gunicorn ใน venv ของคุณ
      args: '--bind 0.0.0.0:9000 --workers 4 --timeout 120 "app:create_app()"',
      cwd: '/home/your-user/meeting-registration', // << แก้ไข path นี้
      interpreter: 'none',
      env: {
        FLASK_ENV: 'production',
        PORT: 9000
        // ใส่ .env variables อื่นๆ ที่จำเป็นที่นี่
      },
      error_file: './logs/pm2-app-error.log',
      out_file: './logs/pm2-app-out.log',
      log_file: './logs/pm2-app-combined.log',
      time: true,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      // --- Process 2: Celery Worker (ส่วนที่เพิ่มเข้ามา) ---
      name: 'meeting-worker',
      script: '/home/your-user/meeting-registration/venv/bin/celery', // << แก้ไข path ไปยัง celery ใน venv
      args: '-A celery_worker.celery_app worker --loglevel=info',
      cwd: '/home/your-user/meeting-registration', // << แก้ไข path นี้
      interpreter: 'none',
      env: {
        FLASK_ENV: 'production'
        // ใส่ .env variables อื่นๆ ที่จำเป็นที่นี่
      },
      error_file: './logs/pm2-worker-error.log',
      out_file: './logs/pm2-worker-out.log',
      log_file: './logs/pm2-worker-combined.log',
      time: true,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M' // Worker อาจใช้ memory น้อยกว่า
    }
  ]
};
```

2. คำสั่ง PM2 แบบ Command Line:

```bash
# วิธีที่ 1: ใช้ Gunicorn (แนะนำสำหรับ Production)
pm2 start gunicorn \
  --name "meeting-registration" \
  --interpreter none \
  -- --bind 0.0.0.0:9000 \
  --workers 4 \
  --timeout 120 \
  --chdir /path/to/meeting-registration \
  "app:create_app('production')"

# วิธีที่ 2: ใช้ Python โดยตรง (สำหรับ Development)
pm2 start app.py \
  --name "meeting-registration" \
  --interpreter python3 \
  --cwd /path/to/meeting-registration \
  -- --port 9000

# วิธีที่ 3: ใช้ ecosystem file
pm2 start ecosystem.config.js
```

คำสั่ง PM2 ที่ใช้บ่อย

```bash
# Start application
pm2 start ecosystem.config.js

# List all processes
pm2 list

# Monitor
pm2 monit

# View logs
pm2 logs meeting-registration
pm2 logs meeting-registration --lines 100

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

Deploy

```python
def create_app(config_name=None):
    """Application factory pattern"""
    
    app = Flask(__name__)
    
    # ถ้ารันผ่าน nginx ที่ /register/
    app.config['APPLICATION_ROOT'] = '/register'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    
    # ... rest of config
```

```bash

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
    # ✅ START: Flask Meeting Registration App
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
   location /register/admin {
      proxy_pass http://flask_meeting_app/admin;
      
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
   # ✅ END: Flask Meeting Registration App
    
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

Run Flask App:

```bash
# Production with Gunicorn
gunicorn --bind 0.0.0.0:9000 --workers 4 "app:create_app('production')"

# หรือ Development
python app.py
```

-- ระบบลงทะเบียนการประชุม (Meeting Registration System)
-- Database Schema สำหรับ PostgreSQL
-- Updated: 2025-09-26

-- ==========================================
-- 1. ตาราง employees - ข้อมูลพนักงาน
-- ==========================================
CREATE TABLE IF NOT EXISTS employees (
    emp_id VARCHAR(20) PRIMARY KEY,
    emp_name VARCHAR(255) NOT NULL,
    position VARCHAR(255),
    section_code VARCHAR(50),
    sec_short VARCHAR(100),
    section_full VARCHAR(255),
    department_code VARCHAR(50),
    department_short VARCHAR(100),
    department_full VARCHAR(255),
    group_code VARCHAR(50),
    group_short VARCHAR(100),
    group_full VARCHAR(255),
    division_code VARCHAR(50),
    division_short VARCHAR(100),
    division_full VARCHAR(255),
    cost_center_code VARCHAR(50),
    cc_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 2. ตาราง users - ผู้จัดการประชุม (Organizers)
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ==========================================
-- 3. ตาราง meetings - ข้อมูลการประชุม
-- ==========================================
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    meeting_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room VARCHAR(100),
    floor VARCHAR(50),
    building VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,  -- การประชุมสาธารณะหรือส่วนตัว
    organizer_id INTEGER REFERENCES users(id),  -- ผู้จัดการประชุม
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 4. ตาราง registrations - การลงทะเบียน
-- ==========================================
CREATE TABLE IF NOT EXISTS registrations (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    emp_id VARCHAR(20) REFERENCES employees(emp_id) ON DELETE SET NULL,
    emp_name VARCHAR(255) NOT NULL,
    position VARCHAR(255),
    sec_short VARCHAR(100),
    cc_name VARCHAR(255),
    registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_manual_entry BOOLEAN DEFAULT FALSE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    UNIQUE(meeting_id, emp_id)  -- ป้องกันการลงทะเบียนซ้ำ
);

-- ==========================================
-- 5. ตาราง otp_tokens - OTP สำหรับ Email Authentication
-- ==========================================
CREATE TABLE IF NOT EXISTS otp_tokens (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(6) NOT NULL,
    purpose VARCHAR(50),  -- 'login' หรือ 'register'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    used BOOLEAN DEFAULT FALSE
);

-- ==========================================
-- INDEXES สำหรับเพิ่มประสิทธิภาพ
-- ==========================================

-- Indexes for employees
CREATE INDEX IF NOT EXISTS idx_employees_emp_id ON employees(emp_id);
CREATE INDEX IF NOT EXISTS idx_employees_emp_name ON employees(emp_name);
CREATE INDEX IF NOT EXISTS idx_employees_cc_name ON employees(cc_name);

-- Indexes for users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Indexes for meetings
CREATE INDEX IF NOT EXISTS idx_meetings_is_active ON meetings(is_active);
CREATE INDEX IF NOT EXISTS idx_meetings_is_public ON meetings(is_public);
CREATE INDEX IF NOT EXISTS idx_meetings_organizer_id ON meetings(organizer_id);
CREATE INDEX IF NOT EXISTS idx_meetings_meeting_date ON meetings(meeting_date);
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at);

-- Indexes for registrations
CREATE INDEX IF NOT EXISTS idx_registrations_meeting_id ON registrations(meeting_id);
CREATE INDEX IF NOT EXISTS idx_registrations_emp_id ON registrations(emp_id);
CREATE INDEX IF NOT EXISTS idx_registrations_registration_time ON registrations(registration_time);

-- Indexes for otp_tokens
CREATE INDEX IF NOT EXISTS idx_otp_tokens_email ON otp_tokens(email);
CREATE INDEX IF NOT EXISTS idx_otp_tokens_token ON otp_tokens(token);
CREATE INDEX IF NOT EXISTS idx_otp_tokens_expires_at ON otp_tokens(expires_at);

-- ==========================================
-- FUNCTIONS และ TRIGGERS
-- ==========================================

-- Function สำหรับอัปเดต updated_at timestamp อัตโนมัติ
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers สำหรับ auto-update timestamp
CREATE TRIGGER update_employees_updated_at 
    BEFORE UPDATE ON employees
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at 
    BEFORE UPDATE ON meetings
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- SAMPLE DATA (Optional - สำหรับทดสอบ)
-- ==========================================

-- สร้าง Admin user ตัวอย่าง (ต้องเปลี่ยน password ใน production)
-- INSERT INTO users (email, name, is_active, is_admin) 
-- VALUES ('admin@example.com', 'System Admin', true, true)
-- ON CONFLICT (email) DO NOTHING;

-- สร้าง Meeting ตัวอย่าง
-- INSERT INTO meetings (topic, meeting_date, start_time, end_time, room, floor, building, is_active, is_public)
-- VALUES ('การประชุมประจำเดือน', CURRENT_DATE + INTERVAL '7 days', '09:00', '12:00', 'ห้องประชุม A', '3', 'อาคาร 1', true, true)
-- ON CONFLICT DO NOTHING;

-- ==========================================
-- GRANT PERMISSIONS (ปรับตาม user ที่ใช้จริง)
-- ==========================================

-- Example: Grant all privileges to application user
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO your_app_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO your_app_user;

-- ==========================================
-- MAINTENANCE QUERIES
-- ==========================================

-- Query สำหรับดู Table sizes
-- SELECT 
--     schemaname AS table_schema,
--     tablename AS table_name,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Query สำหรับดูจำนวน Records
-- SELECT 
--     'employees' as table_name, COUNT(*) as row_count FROM employees
-- UNION ALL
-- SELECT 
--     'users', COUNT(*) FROM users
-- UNION ALL
-- SELECT 
--     'meetings', COUNT(*) FROM meetings
-- UNION ALL
-- SELECT 
--     'registrations', COUNT(*) FROM registrations
-- UNION ALL
-- SELECT 
--     'otp_tokens', COUNT(*) FROM otp_tokens;

-- ==========================================
-- CLEANUP QUERIES (สำหรับ maintenance)
-- ==========================================

-- ลบ OTP tokens ที่หมดอายุแล้ว (ควรรันเป็นประจำ)
-- DELETE FROM otp_tokens WHERE expires_at < CURRENT_TIMESTAMP;

-- ลบ registrations ที่ไม่มี meeting (orphaned records)
-- DELETE FROM registrations WHERE meeting_id NOT IN (SELECT id FROM meetings);
-- สร้างฐานข้อมูลสำหรับระบบลงทะเบียนการประชุม

-- ตาราง employees สำหรับเก็บข้อมูลพนักงาน
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

-- ตาราง meetings สำหรับเก็บข้อมูลการประชุม
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ตาราง registrations สำหรับเก็บข้อมูลการลงทะเบียน
CREATE TABLE IF NOT EXISTS registrations (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id),
    emp_id VARCHAR(20),
    emp_name VARCHAR(255) NOT NULL,
    position VARCHAR(255),
    sec_short VARCHAR(100),
    cc_name VARCHAR(255),
    registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_manual_entry BOOLEAN DEFAULT FALSE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    UNIQUE(meeting_id, emp_id) -- ป้องกันการลงทะเบียนซ้ำ
);

-- สร้าง indexes เพื่อเพิ่มประสิทธิภาพ
CREATE INDEX idx_employees_emp_id ON employees(emp_id);
CREATE INDEX idx_employees_emp_name ON employees(emp_name);
CREATE INDEX idx_registrations_meeting_id ON registrations(meeting_id);
CREATE INDEX idx_registrations_emp_id ON registrations(emp_id);
CREATE INDEX idx_registrations_time ON registrations(registration_time);

-- Trigger สำหรับอัปเดต updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at BEFORE UPDATE ON meetings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

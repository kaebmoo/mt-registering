-----

# ระบบลงทะเบียนการประชุม (Meeting Registration System)

โปรเจกต์นี้เป็นเว็บแอปพลิเคชันที่สร้างด้วย PHP สำหรับใช้เป็นระบบลงทะเบียนเข้าร่วมการประชุม โดยมีฟังก์ชันหลักคือการแสดงรายละเอียดการประชุม, ให้ผู้เข้าร่วมลงทะเบียนด้วยรหัสพนักงาน, และมีระบบหลังบ้านสำหรับเจ้าหน้าที่เพื่อแก้ไขข้อมูลการประชุม

ข้อมูลการลงทะเบียนทั้งหมดจะถูกส่งไปยัง Google Apps Script เพื่อบันทึกลงใน Google Sheets แบบเรียลไทม์

## ✨ คุณสมบัติ (Features)

  * **แสดงรายละเอียดการประชุม**: แสดงหัวข้อ, วันที่, เวลา, และสถานที่ของการประชุมบนหน้าแรก
  * **ลงทะเบียนด้วยรหัสพนักงาน**: ผู้ใช้สามารถกรอกรหัสพนักงานเพื่อดึงข้อมูลจากฐานข้อมูล SQLite และทำการลงทะเบียน
  * **ลงทะเบียนด้วยตนเอง**: ในกรณีที่ไม่พบรหัสพนักงานในระบบ ผู้ใช้สามารถกรอกข้อมูลเพื่อลงทะเบียนด้วยตนเองได้
  * **เชื่อมต่อกับ Google Sheets**: ทุกการลงทะเบียนที่สำเร็จจะถูกส่งข้อมูลไปยัง Google Apps Script Endpoint
  * **ระบบจัดการหลังบ้าน**:
      * มีหน้าล็อกอินสำหรับเจ้าหน้าที่ (`/admin`)
      * เจ้าหน้าที่สามารถแก้ไขรายละเอียดของการประชุมได้
      * รหัสผ่านถูกจัดเก็บอย่างปลอดภัยด้วยการ Hashing
  * **การจัดการฐานข้อมูล**: ระบบจะดาวน์โหลดไฟล์ฐานข้อมูล SQLite จาก URL ที่กำหนดใน Environment Variable โดยอัตโนมัติหากยังไม่มีไฟล์ในระบบ เพื่อความสะดวกในการ развертывание

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
.
├── Dockerfile
├── admin
│   ├── detail.php        # หน้าแก้ไขรายละเอียดการประชุม
│   ├── download_db.php   # สคริปต์ดาวน์โหลด DB สำหรับส่วน admin
│   ├── index.html        # ทำหน้าที่ redirect ไปยังหน้า login
│   └── login.php         # หน้าล็อกอินสำหรับเจ้าหน้าที่
├── download_db.php         # สคริปต์ดาวน์โหลด DB สำหรับส่วนหน้าบ้าน
├── index.html              # หน้าแรก แสดงข้อมูลและฟอร์มลงทะเบียน
├── register.php            # สคริปต์ประมวลผลการลงทะเบียน (ค้นหาจาก DB)
├── register_manual.php     # สคริปต์ประมวลผลการลงทะเบียน (กรอกข้อมูลเอง)
└── router.php              # Router สำหรับ PHP built-in server (ใช้ตอนพัฒนา)
```

## 🛠️ การตั้งค่าและการติดตั้ง (Setup and Installation)

### ข้อกำหนดเบื้องต้น (Prerequisites)

  * Docker และ Docker Compose
  * (หรือ) PHP 8.0+ พร้อม extension `pdo_sqlite` สำหรับการรันบนเครื่องโดยตรง

### การกำหนดค่า (Configuration)

โปรเจกต์นี้ต้องการ Environment Variables 2 ตัวเพื่อทำงาน:

1.  **`DB_URL`**: URL สำหรับดาวน์โหลดไฟล์ฐานข้อมูล SQLite (`.db`) ที่มีตาราง `employee`, `schedule`, และ `users`
2.  **Google Apps Script URL**: URL ของ Web App ที่สร้างจาก Google Apps Script ซึ่งฮาร์ดโค้ดไว้ในไฟล์ `register.php` และ `register_manual.php` คุณจำเป็นต้องแก้ไข URL นี้ให้เป็นของคุณ

#### ขั้นตอนการตั้งค่า

1.  **สร้างไฟล์ `.env`**
    สร้างไฟล์ชื่อ `.env` ใน root directory ของโปรเจกต์ และใส่ URL สำหรับดาวน์โหลดฐานข้อมูลของคุณ:

    ```env
    DB_URL="https://your-public-url.com/path/to/RegisterForm.db"
    ```

2.  **(แนะนำ) แก้ไข Google Apps Script URL**
    เปิดไฟล์ `register.php` และ `register_manual.php` และแก้ไขตัวแปร `$url` ให้เป็น URL ของคุณ:

    ```php
    // ใน register.php และ register_manual.php
    $url = "https://script.google.com/macros/s/YOUR_APPS_SCRIPT_ID/exec";
    ```

### การรันโปรเจกต์ผ่าน Docker (แนะนำ)

1.  **สร้างไฟล์ `docker-compose.yml`**:

    ```yaml
    version: '3.8'

    services:
      web:
        build:
          context: .
          dockerfile: Dockerfile
        ports:
          - "8080:80"
        volumes:
          - .:/var/www/html
        env_file:
          - .env
        environment:
          # ส่งผ่านค่าจาก .env ไปยัง PHP
          - DB_URL=${DB_URL}
    ```

2.  **รัน Docker Container**:

    ```bash
    docker-compose up -d --build
    ```

3.  **เข้าใช้งาน**:

      * หน้าลงทะเบียน: [http://localhost:8080](https://www.google.com/search?q=http://localhost:8080)
      * หน้าสำหรับเจ้าหน้าที่: [http://localhost:8080/admin](https://www.google.com/search?q=http://localhost:8080/admin)

### การรันโปรเจกต์ผ่าน PHP Built-in Server (สำหรับพัฒนา)

1.  **ตั้งค่า Environment Variable**:

    ```bash
    # บน Linux/macOS
    export DB_URL="https://your-public-url.com/path/to/RegisterForm.db"

    # บน Windows (Command Prompt)
    set DB_URL="https://your-public-url.com/path/to/RegisterForm.db"
    ```

2.  **เริ่ม Server**:
    ใช้ `router.php` เพื่อจัดการ request ทั้งหมด

    ```bash
    php -S localhost:8000 router.php
    ```

3.  **เข้าใช้งาน**:

      * หน้าลงทะเบียน: [http://localhost:8000](https://www.google.com/search?q=http://localhost:8000)
      * หน้าสำหรับเจ้าหน้าที่: [http://localhost:8000/admin](https://www.google.com/search?q=http://localhost:8000/admin)

## 🗃️ โครงสร้างฐานข้อมูล (Database Schema)

ไฟล์ฐานข้อมูล SQLite (`RegisterForm.db`) ควรมีโครงสร้างตารางดังนี้:

  * **`employee`**: ตารางข้อมูลพนักงาน

      * `emp_id` (TEXT, PRIMARY KEY): รหัสพนักงาน
      * `emp_name` (TEXT): ชื่อ-นามสกุล
      * `position` (TEXT): ตำแหน่ง
      * `sec_short` (TEXT): ส่วนงาน (ย่อ)
      * `cc_name` (TEXT): ชื่อศูนย์ต้นทุน

  * **`schedule`**: ตารางข้อมูลรายละเอียดการประชุม (ควรมีเพียง 1 แถว)

      * `id` (INTEGER, PRIMARY KEY): ID ของรายการ (ใช้ค่าเป็น 1)
      * `topic` (TEXT): หัวข้อการประชุม
      * `date` (TEXT): วันที่ (เช่น 30 มิถุนายน 2568)
      * `start_time` (TEXT): เวลาเริ่ม (HH:MM)
      * `end_time` (TEXT): เวลาสิ้นสุด (HH:MM)
      * `room` (TEXT): ห้องประชุม
      * `floor` (TEXT): ชั้น
      * `building` (TEXT): อาคาร/สถานที่

  * **`users`**: ตารางข้อมูลผู้ใช้งานระบบ (สำหรับเจ้าหน้าที่)

      * `username` (TEXT, UNIQUE): ชื่อผู้ใช้
      * `password` (TEXT): รหัสผ่าน (เก็บในรูปแบบ Hashed ด้วย `password_hash`)
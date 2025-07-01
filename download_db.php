<?php
/**
 * ไฟล์สำหรับเชื่อมต่อฐานข้อมูล SQLite
 * จะมองหาไฟล์ RegisterForm.db ที่อยู่ในไดเรกทอรีเดียวกับไฟล์นี้
 */

// กำหนด path ไปยังไฟล์ฐานข้อมูลที่อยู่ใน root ของ project
// __DIR__ จะหมายถึงไดเรกทอรีปัจจุบันของไฟล์นี้ (เช่น /var/www/register-app)
$dbPath = __DIR__ . '/RegisterForm.db';

// ตรวจสอบว่าไฟล์ฐานข้อมูลมีอยู่จริงหรือไม่
if (!file_exists($dbPath)) {
    // ถ้าไม่มีไฟล์ ให้หยุดการทำงานและแสดงข้อความผิดพลาดที่ชัดเจน
    // ทำให้คุณรู้ทันทีว่าลืมวางไฟล์ RegisterForm.db ไว้ในโปรเจกต์
    exit("ERROR: ไม่พบไฟล์ฐานข้อมูล 'RegisterForm.db' ในโปรเจกต์ กรุณาตรวจสอบว่าวางไฟล์ไว้ถูกต้อง");
}

try {
    // เชื่อมต่อกับไฟล์ SQLite โดยใช้ path ที่กำหนด
    $db = new PDO('sqlite:' . $dbPath);

    // ตั้งค่าให้ PDO แสดงข้อผิดพลาดแบบ Exception เพื่อให้จัดการง่าย
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

} catch (PDOException $e) {
    // หากการเชื่อมต่อล้มเหลว ให้แสดงข้อความผิดพลาด
    exit("เชื่อมต่อฐานข้อมูลล้มเหลว: " . htmlspecialchars($e->getMessage()));
}
?>
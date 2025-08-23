<?php
// admin/admin_config.php
/**
 * ไฟล์สำหรับเก็บข้อมูลผู้ดูแลระบบ
 * รหัสผ่านเริ่มต้นสำหรับ 'admin' คือ 'password1234' => '$2y$10$L2oX8ldrgQx3pGpbSg9jX.msJ9S2jGgRvoGzB3R.n7dG4H6/y5Q.S'
 * หากต้องการเพิ่มผู้ใช้ ให้เพิ่ม key ใหม่และ hash รหัสผ่าน
 * สามารถสร้าง hash ได้ที่: https://www.phppasswordhash.com/
 */

return [
    'nt.transferprice@gmail.com' => '$2y$12$qFBcbyZ4DkrB28S.FJk/9uuO7xpbA/H.zunxlqOKGYbEGjM6Lp16K'
    // ตัวอย่างการเพิ่ม user คนที่สอง:
    // 'user2' => 'HASH_ของ_รหัสผ่าน_user2'
];

?>
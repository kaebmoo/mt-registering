<?php
// admin/logout.php

session_start(); // เริ่ม session

// ลบตัวแปร session ทั้งหมด
session_unset();

// ทำลาย session
session_destroy();

// กลับไปยังหน้า login
header("Location: login.php");
exit();
?>

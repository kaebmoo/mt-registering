<?php
session_start();

// ตรวจสอบ session ถ้ายังไม่ได้ล็อกอิน ให้กลับไปหน้า login
if (!isset($_SESSION["user"])) {
    header("Location: login.php");
    exit();
}

// กำหนดตำแหน่งไฟล์ schedule.json ที่อยู่ด้านนอกโฟลเดอร์ admin
$schedule_file = __DIR__ . '/../schedule.json';
$success = false;

// เมื่อกดปุ่มบันทึก (POST)
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // สร้าง array ของข้อมูลใหม่จากฟอร์ม
    $new_schedule_data = [
        'topic'      => $_POST['topic'] ?? '',
        'date'       => $_POST['date'] ?? '',
        'start_time' => $_POST['start_time'] ?? '',
        'end_time'   => $_POST['end_time'] ?? '',
        'room'       => $_POST['room'] ?? '',
        'floor'      => $_POST['floor'] ?? '',
        'building'   => $_POST['building'] ?? '',
    ];

    // แปลง array เป็น JSON และบันทึกลงไฟล์
    $json_content = json_encode($new_schedule_data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    
    if (file_put_contents($schedule_file, $json_content)) {
        $success = true;
    }
}

// ดึงข้อมูลการประชุมจากไฟล์ JSON มาแสดง
$schedule = [];
if (file_exists($schedule_file)) {
    $schedule_json = file_get_contents($schedule_file);
    $schedule = json_decode($schedule_json, true);
}
?>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>รายละเอียดการประชุม</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<div class="ui container" style="padding: 30px 0;">
    <h2 class="ui header">แก้ไขรายละเอียดการประชุม (ผู้ใช้: <?= htmlspecialchars($_SESSION['user']) ?>)</h2>

    <?php if ($success): ?>
        <div class="ui green message">บันทึกข้อมูลลงใน <code>schedule.json</code> สำเร็จ</div>
    <?php endif; ?>

    <form class="ui form" method="POST" action="">
        <div class="field">
            <label>หัวข้อการประชุม</label>
            <input type="text" name="topic" value="<?= htmlspecialchars($schedule['topic'] ?? '') ?>" required>
        </div>
        <div class="three fields">
            <div class="field">
                <label>วันที่ <span style="color: gray;">(เช่น 15 กรกฎาคม 2568)</span></label>
                <input type="text" name="date" value="<?= htmlspecialchars($schedule['date'] ?? '') ?>" required>
            </div>
            <div class="field">
                <label>เวลาเริ่ม</label>
                <input type="time" name="start_time" value="<?= htmlspecialchars($schedule['start_time'] ?? '') ?>" required>
            </div>
            <div class="field">
                <label>เวลาสิ้นสุด</label>
                <input type="time" name="end_time" value="<?= htmlspecialchars($schedule['end_time'] ?? '') ?>" required>
            </div>
        </div>
        <div class="three fields">
            <div class="field">
                <label>ห้อง</label>
                <input type="text" name="room" value="<?= htmlspecialchars($schedule['room'] ?? '') ?>">
            </div>
            <div class="field">
                <label>ชั้น</label>
                <input type="text" name="floor" value="<?= htmlspecialchars($schedule['floor'] ?? '') ?>">
            </div>
            <div class="field">
                <label>สถานที่ <span style="color: gray;">(เช่น อาคารสำนักงานใหญ่)</span></label>
                <input type="text" name="building" value="<?= htmlspecialchars($schedule['building'] ?? '') ?>">
            </div>
        </div>
        <button class="ui primary button" type="submit">บันทึก</button>
        <a href="logout.php" class="ui button">ออกจากระบบ</a>
    </form>
</div>
</body>
</html>

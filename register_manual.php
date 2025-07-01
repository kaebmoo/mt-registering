<?php
// register_manual.php
// หน้าสำหรับรับข้อมูลและแสดงผลเมื่อผู้ใช้กรอกข้อมูลด้วยตนเอง

$new_emp_id = '';
$new_emp_name = '';
$new_position = '';
$new_sec_short = '';
$new_cc_name = '';
$error = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $new_emp_id = $_POST['new_emp_id'] ?? ''; 
    $new_emp_name = $_POST['new_emp_name'] ?? '';
    $new_position = $_POST['new_position'] ?? '';
    $new_sec_short = $_POST['new_sec_short'] ?? '';
    $new_cc_name = $_POST['new_cc_name'] ?? '';

    // ทำการตรวจสอบข้อมูลพื้นฐาน
    if (strlen($new_emp_id) < 6) {
        $error = 'รหัสพนักงานต้องมีอย่างน้อย 6 หลัก';
    } elseif (empty($new_emp_name)) {
        $error = 'กรุณากรอกชื่อ-นามสกุล';
    }

    // ถ้าไม่มีข้อผิดพลาด ให้ส่งข้อมูลไป Google Apps Script
    if (empty($error)) {
        $url = "https://script.google.com/macros/s/AKfycbyQcNpLCgjbeVAfGZwmK9suB5OuWPyGl2W5UJ98tIqumUk2-Yu9w9a-UzhjTjhtvcM/exec"; 
        $data = [
            'รหัสพนักงาน' => $new_emp_id, 
            'ชื่อ' => $new_emp_name,
            'ตำแหน่ง' => $new_position,
            'ส่วนงานย่อ' => $new_sec_short,
            'ชื่อศูนย์ต้นทุน' => $new_cc_name, 
        ];

        $options = [
            'http' => [
                'header'  => "Content-type: application/json",
                'method'  => 'POST',
                'content' => json_encode($data),
                'ignore_errors' => true
            ],
        ];

        $context = stream_context_create($options);
        @file_get_contents($url, false, $context);
    }
} 
?>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>ผลการลงทะเบียนด้วยตนเอง</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { padding: 40px; background-color: #f9f9f9; }
        .ui.list .item .header { font-weight: bold; }
        .ui.list .item .description { color: #555; }
    </style>
</head>
<body>
<div class="ui container">
    
<?php if ($_SERVER["REQUEST_METHOD"] == "POST" && empty($error)): ?>
    
    <!-- START: ปรับปรุงการแสดงผลเมื่อสำเร็จ -->
    <div class="ui icon positive message">
        <i class="check circle outline icon"></i>
        <div class="content">
            <div class="header">ลงทะเบียนด้วยตนเองสำเร็จ</div>
            <p>ข้อมูลของคุณได้ถูกบันทึกเรียบร้อยแล้ว</p>
        </div>
    </div>

    <div class="ui segment">
        <h3 class="ui header">ข้อมูลที่บันทึก</h3>
        <div class="ui relaxed divided list">
            <div class="item">
                <i class="large id card outline middle aligned icon"></i>
                <div class="content">
                    <div class="header">รหัสพนักงาน</div>
                    <div class="description"><?= htmlspecialchars($new_emp_id) ?></div>
                </div>
            </div>
            <div class="item">
                <i class="large user outline middle aligned icon"></i>
                <div class="content">
                    <div class="header">ชื่อ</div>
                    <div class="description"><?= htmlspecialchars($new_emp_name) ?></div>
                </div>
            </div>
            <div class="item">
                <i class="large briefcase middle aligned icon"></i>
                <div class="content">
                    <div class="header">ตำแหน่ง</div>
                    <div class="description"><?= htmlspecialchars($new_position ?: 'ไม่ระบุ') ?></div>
                </div>
            </div>
            <div class="item">
                <i class="large sitemap middle aligned icon"></i>
                <div class="content">
                    <div class="header">ส่วนงานย่อ</div>
                    <div class="description"><?= htmlspecialchars($new_sec_short ?: 'ไม่ระบุ') ?></div>
                </div>
            </div>
            <div class="item">
                <i class="large building outline middle aligned icon"></i>
                <div class="content">
                    <div class="header">ชื่อศูนย์ต้นทุน</div>
                    <div class="description"><?= htmlspecialchars($new_cc_name ?: 'ไม่ระบุ') ?></div>
                </div>
            </div>
        </div>
    </div>
    <a href="index.php" class="ui huge primary icon labeled button"><i class="home icon"></i> กลับหน้าแรก</a>
    <!-- END: ปรับปรุงการแสดงผลเมื่อสำเร็จ -->

<?php elseif (!empty($error)): ?>

    <!-- START: การแสดงผลเมื่อเกิดข้อผิดพลาด -->
    <div class="ui icon negative message">
        <i class="exclamation triangle icon"></i>
        <div class="content">
            <div class="header">เกิดข้อผิดพลาด</div>
            <p><?= htmlspecialchars($error) ?></p>
        </div>
    </div>
    <div class="ui button" onclick="window.history.back()">
        <i class="arrow left icon"></i>
        ย้อนกลับไปแก้ไข
    </div>
    <!-- END: การแสดงผลเมื่อเกิดข้อผิดพลาด -->

<?php else: ?>
    
    <!-- กรณีเข้าหน้านี้โดยตรง (ไม่ใช่ POST) -->
    <div class="ui icon warning message">
        <i class="info circle icon"></i>
        <div class="content">
            <div class="header">ไม่พบข้อมูล</div>
            <p>กรุณากลับไปที่หน้าลงทะเบียนหลัก</p>
        </div>
    </div>
    <a href="index.php" class="ui primary button">กลับหน้าแรก</a>

<?php endif; ?>

</div>
</body>
</html>

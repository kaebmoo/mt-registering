<?php
session_start(); 
ob_start();

$error = "";
$users_file = __DIR__ . '/users.json';

// 1. ตรวจสอบว่ามีไฟล์ users.json หรือไม่
if (!file_exists($users_file)) {
    $error = "เกิดข้อผิดพลาด: ไม่พบไฟล์ข้อมูลผู้ใช้ (users.json)";
} else {
    // 2. อ่านและถอดรหัสข้อมูลจากไฟล์ JSON
    $json_data = file_get_contents($users_file);
    $users = json_decode($json_data, true);

    // 3. ตรวจสอบเมื่อมีการส่งฟอร์ม
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $username = $_POST["username"] ?? '';
        $password = $_POST["password"] ?? '';

        // 4. ตรวจสอบว่ามีชื่อผู้ใช้นี้ใน array หรือไม่
        if (isset($users[$username])) {
            // 5. ตรวจสอบรหัสผ่านที่ hash ไว้
            if (password_verify($password, $users[$username])) {
                // ถ้ารหัสผ่านถูกต้อง ให้สร้าง session และไปหน้า detail
                $_SESSION["user"] = $username;
                header("Location: detail.php");
                exit();
            } else {
                $error = "รหัสผ่านไม่ถูกต้อง";
            }
        } else {
            $error = "ไม่พบชื่อผู้ใช้นี้ในระบบ";
        }
    }
}
?>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>เข้าสู่ระบบเจ้าหน้าที่</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #f0f2f5; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .ui.container { max-width: 400px !important; }
    </style>
</head>
<body>
<div class="ui container">
    <div class="ui middle aligned center aligned grid">
        <div class="column">
            <h2 class="ui image header">
                <div class="content">เข้าสู่ระบบส่วนผู้ดูแล</div>
            </h2>
            <form class="ui large form" method="POST" action="">
                <div class="ui stacked segment">
                    <div class="field">
                        <div class="ui left icon input">
                            <i class="user icon"></i>
                            <input type="text" name="username" placeholder="ชื่อผู้ใช้" required>
                        </div>
                    </div>
                    <div class="field">
                        <div class="ui left icon input">
                            <i class="lock icon"></i>
                            <input type="password" name="password" placeholder="รหัสผ่าน" required>
                        </div>
                    </div>
                    <button class="ui fluid large primary submit button" type="submit">เข้าสู่ระบบ</button>
                </div>
                <?php if (!empty($error)): ?>
                    <div class="ui error message" style="display:block;"><?= htmlspecialchars($error) ?></div>
                <?php endif; ?>
            </form>
        </div>
    </div>
</div>
</body>
</html>

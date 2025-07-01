<?php
// register.php

// โหลดไฟล์ .env สำหรับเก็บค่า Configuration
/*
require_once __DIR__ . '/vendor/autoload.php';
try {
    $dotenv = Dotenv\Dotenv::createImmutable(__DIR__ . '/config');
    $dotenv->load();
} catch (\Dotenv\Exception\InvalidPathException $e) {
    // ไม่ต้องทำอะไรถ้าไม่พบไฟล์ .env, โค้ดจะใช้ค่า null แทน
}
*/

// ฟังก์ชันสำหรับโหลดข้อมูลพนักงาน (พร้อมระบบแคชหลายระดับ)
function get_employee_data() {
    $cache_key = 'employee_data_map';
    $cache_file = __DIR__ . '/cache/employee_cache.php';
    
    // ตรวจสอบก่อนว่าส่วนเสริม APCu ใช้งานได้หรือไม่
    $is_apcu_enabled = function_exists('apcu_fetch');

    // 1. ถ้า APCu ใช้งานได้, ให้ลองดึงข้อมูลจากแคชก่อน
    if ($is_apcu_enabled) {
        $employee_map = apcu_fetch($cache_key);
        if ($employee_map !== false) {
            return $employee_map;
        }
    }

    // 2. ลอง File Cache (เร็วกว่าอ่าน CSV เสมอ)
    if (file_exists($cache_file)) {
        $csvFile = __DIR__ . '/employee.csv';
        if (!file_exists($csvFile) || filemtime($cache_file) > filemtime($csvFile)) {
            // Cache file ใหม่กว่า CSV file
            $cached_data = include $cache_file;
            if (is_array($cached_data) && !empty($cached_data)) {
                // ถ้า APCu ใช้งานได้ เก็บลง memory cache ด้วย
                if ($is_apcu_enabled) {
                    apcu_store($cache_key, $cached_data, 3600);
                }
                return $cached_data;
            }
        }
    }

    // 3. อ่านจากไฟล์ CSV (เป็นทางเลือกสุดท้าย)
    $csvFile = __DIR__ . '/employee.csv';
    if (!file_exists($csvFile)) {
        throw new Exception("ไม่พบไฟล์ข้อมูลพนักงาน (employee.csv)");
    }

    $employee_map = [];
    
    // ใช้ SplFileObject เพื่อประสิทธิภาพที่ดีกว่า
    $file = new SplFileObject($csvFile);
    $file->setFlags(SplFileObject::READ_CSV | SplFileObject::SKIP_EMPTY);
    
    $headers = $file->fgetcsv(); // อ่านบรรทัดแรกเป็น Header
    
    foreach ($file as $data) {
        // ตรวจสอบข้อมูลเบื้องต้น
        if (is_array($data) && count($headers) == count($data)) {
            $row = array_combine($headers, $data);
            // ใช้ emp_id เป็น key และทำ normalization
            $emp_id = trim($row['emp_id']);
            $employee_map[$emp_id] = [
                'emp_id' => $emp_id,
                'emp_name' => trim($row['emp_name'] ?? ''),
                'position' => trim($row['position'] ?? ''),
                'sec_short' => trim($row['sec_short'] ?? ''),
                'cc_name' => trim($row['cc_name'] ?? '')
            ];
        }
    }

    // 4. สร้าง cache directory ถ้ายังไม่มี
    $cache_dir = dirname($cache_file);
    if (!is_dir($cache_dir)) {
        mkdir($cache_dir, 0755, true);
    }

    // 5. เก็บลง File Cache (รูปแบบ PHP array ที่ประมวลผลเร็ว)
    $cache_content = "<?php\n// Auto-generated cache file - " . date('Y-m-d H:i:s') . "\n";
    $cache_content .= "return " . var_export($employee_map, true) . ";\n";
    file_put_contents($cache_file, $cache_content, LOCK_EX);

    // 6. เก็บลง APCu ถ้าใช้งานได้
    if ($is_apcu_enabled) {
        apcu_store($cache_key, $employee_map, 3600);
    }

    return $employee_map;
}

// ฟังก์ชันสำหรับค้นหาพนักงาน
function search_employee($emp_id, $employee_data) {
    $emp_id = trim($emp_id);
    
    if (strlen($emp_id) < 6) {
        return null;
    }
    
    // 1. ค้นหาแบบตรงกัน
    if (isset($employee_data[$emp_id])) {
        return $employee_data[$emp_id];
    }
    
    // 2. ลบ 0 นำหน้า
    $emp_id_no_leading = ltrim($emp_id, '0');
    if (strlen($emp_id_no_leading) >= 6 && isset($employee_data[$emp_id_no_leading])) {
        return $employee_data[$emp_id_no_leading];
    }
    
    return null;
}

?>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>ผลการลงทะเบียน</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { padding: 40px; background-color: #f9f9f9; }
        .performance-info { 
            background: #f0f0f0; padding: 10px; margin-top: 20px; 
            border-radius: 4px; font-size: 0.9em; color: #666;
            word-wrap: break-word;
        }
        .ui.list .item .header { font-weight: bold; }
        .ui.list .item .description { color: #555; }
    </style>
</head>
<body>
<div class="ui container">

<?php
// --- ส่วนหลักของโปรแกรม ---
error_reporting(E_ALL & ~E_DEPRECATED);

$start_time = microtime(true);
$emp_id = $_POST['emp_id'] ?? '';
$row = null;

try {
    if (empty($emp_id)) {
        throw new Exception("กรุณากรอกรหัสพนักงาน");
    }
    
    $employee_data = get_employee_data();
    $row = search_employee($emp_id, $employee_data);
    
    if ($row) {
        // --- START: ปรับปรุงการแสดงผลเมื่อสำเร็จ ---
?>
        <div class="ui icon positive message">
            <i class="check circle outline icon"></i>
            <div class="content">
                <div class="header">ลงทะเบียนสำเร็จ</div>
                <p>ข้อมูลของคุณได้ถูกบันทึกเรียบร้อยแล้ว</p>
            </div>
        </div>

        <div class="ui segment">
            <h3 class="ui header">ข้อมูลผู้ลงทะเบียน</h3>
            <div class="ui relaxed divided list">
                <div class="item">
                    <i class="large id card outline middle aligned icon"></i>
                    <div class="content"><div class="header">รหัสพนักงาน</div><div class="description"><?= htmlspecialchars($row['emp_id']) ?></div></div>
                </div>
                <div class="item">
                    <i class="large user outline middle aligned icon"></i>
                    <div class="content"><div class="header">ชื่อ</div><div class="description"><?= htmlspecialchars($row['emp_name']) ?></div></div>
                </div>
                <div class="item">
                    <i class="large briefcase middle aligned icon"></i>
                    <div class="content"><div class="header">ตำแหน่ง</div><div class="description"><?= htmlspecialchars($row['position'] ?? 'ไม่ระบุ') ?></div></div>
                </div>
                <div class="item">
                    <i class="large sitemap middle aligned icon"></i>
                    <div class="content"><div class="header">ส่วนงานย่อ</div><div class="description"><?= htmlspecialchars($row['sec_short'] ?? 'ไม่ระบุ') ?></div></div>
                </div>
                <div class="item">
                    <i class="large building outline middle aligned icon"></i>
                    <div class="content"><div class="header">ชื่อหน่วยงาน</div><div class="description"><?= htmlspecialchars($row['cc_name'] ?? 'ไม่ระบุ') ?></div></div>
                </div>
            </div>
        </div>
        <a href="index.php" class="ui huge primary icon labeled button"><i class="home icon"></i> กลับหน้าแรก</a>
<?php
        // --- END: ปรับปรุงการแสดงผลเมื่อสำเร็จ ---

        // ส่งข้อมูลไป Google Sheets
        // $url = $_ENV['GOOGLE_SCRIPT_URL'] ?? null;

        $url = "https://script.google.com/macros/s/AKfycbyQcNpLCgjbeVAfGZwmK9suB5OuWPyGl2W5UJ98tIqumUk2-Yu9w9a-UzhjTjhtvcM/exec";
        $data_to_send = ['รหัสพนักงาน' => $row['emp_id'], 'ชื่อ' => $row['emp_name'], 'ตำแหน่ง' => $row['position'], 'ส่วนงานย่อ' => $row['sec_short'], 'ชื่อศูนย์ต้นทุน' => $row['cc_name']];
        $options = ['http' => ['header'  => "Content-type: application/json\r\n", 'method'  => 'POST', 'content' => json_encode($data_to_send), 'timeout' => 5]];
        $context = stream_context_create($options);
        $result = @file_get_contents($url, false, $context);
    
    } else {
        // --- START: ปรับปรุงการแสดงผลเมื่อไม่สำเร็จ (รวมทุกกรณี) ---
?>
        <div class="ui segment">
            <?php
            if (strlen($emp_id) < 6) {
                $error_header = 'รหัสพนักงานไม่ถูกต้อง';
                $error_message = 'รหัสพนักงานต้องมีอย่างน้อย 6 หลัก คุณใส่ "' . htmlspecialchars($emp_id) . '" (' . strlen($emp_id) . ' หลัก)';
            } else {
                $error_header = 'ไม่พบข้อมูลพนักงาน';
                $error_message = 'ไม่พบรหัสพนักงาน "' . htmlspecialchars($emp_id) . '" ในระบบ';
            }
            ?>
            <div class="ui icon negative message">
                <i class="times circle outline icon"></i>
                <div class="content">
                    <div class="header"><?= $error_header ?></div>
                    <p><?= $error_message ?></p>
                </div>
            </div>

            <h3 class="ui dividing header">
                <i class="keyboard outline icon"></i>
                <div class="content">
                    กรอกข้อมูลด้วยตนเอง
                    <div class="sub header">ในกรณีที่ค้นหาข้อมูลไม่พบ หรือต้องการแก้ไข</div>
                </div>
            </h3>
            
            <form class="ui form" name="addform" method="POST" action="register_manual.php">
                <div class="field">
                    <label>รหัสพนักงาน <span style="color: gray;">(กรุณาตรวจสอบให้ถูกต้อง)</span></label>
                    <input type="text" name="new_emp_id" value="<?= htmlspecialchars($emp_id) ?>" required minlength="6">
                </div>
                <div class="field">
                    <label>ชื่อ-นามสกุล</label>
                    <input type="text" name="new_emp_name" required>
                </div>
                <div class="field">
                    <label>ตำแหน่ง <span style="color: gray;">(ถ้ามี)</span></label>
                    <input type="text" name="new_position">
                </div>
                <div class="field">
                    <label>ส่วนงานย่อ <span style="color: gray;">(ถ้ามี)</span></label>
                    <input type="text" name="new_sec_short">
                </div>
                <div class="field">
                    <label>ชื่อหน่วยงาน <span style="color: gray;">(ถ้ามี)</span></label>
                    <input type="text" name="new_cc_name">
                </div>
                <div style="margin-top: 20px;">
                    <button class="ui primary icon labeled button" type="submit">
                        <i class="paper plane outline icon"></i>
                        ลงทะเบียน
                    </button>
                    <div class="ui button" onclick="window.history.back()">
                        <i class="arrow left icon"></i>
                        ย้อนกลับ
                    </div>
                </div>
            </form>
        </div>
<?php
        // --- END: ปรับปรุงการแสดงผลเมื่อไม่สำเร็จ ---
    }

    // แสดงข้อมูล Performance (เฉพาะในโหมด debug)
    if (isset($_GET['debug'])) {
        echo '<div class="performance-info">';
        echo "<b>📊 Performance:</b> ";
        echo "Total Time: " . number_format((microtime(true) - $start_time) * 1000, 2) . "ms | ";
        echo "Employees: " . number_format(count($employee_data));
        
        if (function_exists('apcu_fetch') && apcu_fetch('employee_data_map') !== false) {
            echo " | Cache: APCu ✅";
        } elseif (file_exists(__DIR__ . '/cache/employee_cache.php')) {
            echo " | Cache: File 📁";
        } else {
            echo " | Cache: None (Read from CSV) 📄";
        }
        echo '</div>';
    }

} catch (Exception $e) {
    echo '<div class="ui error icon message"><i class="exclamation triangle icon"></i><div class="content"><div class="header">เกิดข้อผิดพลาด</div><p>' . htmlspecialchars($e->getMessage()) . '</p></div></div>';
}
?>
</div>
</body>
</html>

<?php
// register.php

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
    $file->setFlags(SplFileObject::READ_CSV);
    
    $headers = null;
    $line_count = 0;
    
    foreach ($file as $data) {
        if ($line_count === 0) {
            $headers = $data;
            $line_count++;
            continue;
        }
        
        // ข้าม empty lines
        if (empty($data) || !isset($data[0]) || trim($data[0]) === '') {
            continue;
        }
        
        // ตรวจสอบข้อมูลเบื้องต้น
        if (count($headers) == count($data)) {
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
        $line_count++;
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

// ฟังก์ชันสำหรับค้นหาพนักงานแบบ Fuzzy Search
function search_employee($emp_id, $employee_data) {
    $emp_id = trim($emp_id);
    
    // 1. ค้นหาแบบตรงกัน exact match
    if (isset($employee_data[$emp_id])) {
        return $employee_data[$emp_id];
    }
    
    // 2. ลบ leading zeros แล้วลองอีกครั้ง
    $emp_id_no_leading = ltrim($emp_id, '0');
    if ($emp_id_no_leading && isset($employee_data[$emp_id_no_leading])) {
        return $employee_data[$emp_id_no_leading];
    }
    
    // 3. ใส่ leading zeros แล้วลองหา (กรณี user ไม่ใส่ 0 ด้านหน้า)
    $padded_variations = [
        str_pad($emp_id, 4, '0', STR_PAD_LEFT),
        str_pad($emp_id, 5, '0', STR_PAD_LEFT),
        str_pad($emp_id, 6, '0', STR_PAD_LEFT),
        str_pad($emp_id, 7, '0', STR_PAD_LEFT)
    ];
    
    foreach ($padded_variations as $variation) {
        if (isset($employee_data[$variation])) {
            return $employee_data[$variation];
        }
    }
    
    // 4. ถ้ายังไม่เจอ ลองค้นหาใน value (ช้ากว่า แต่ครอบคลุมมากกว่า)
    foreach ($employee_data as $key => $row) {
        if (strpos($key, $emp_id) !== false || strpos($emp_id, $key) !== false) {
            return $row;
        }
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
            background: #f0f0f0; 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 4px; 
            font-size: 0.9em; 
            color: #666;
        }
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
    // เรียกใช้ฟังก์ชันเพื่อเอาข้อมูลพนักงาน
    $load_start = microtime(true);
    $employee_data = get_employee_data();
    $load_time = microtime(true) - $load_start;

    // ค้นหาพนักงานด้วย Fuzzy Search
    $search_start = microtime(true);
    $row = search_employee($emp_id, $employee_data);
    $search_time = microtime(true) - $search_start;
    
    $total_time = microtime(true) - $start_time;
    
    // แสดงข้อมูล Performance (เฉพาะในโหมด debug)
    if (isset($_GET['debug']) || isset($_POST['debug'])) {
        echo '<div class="performance-info">';
        echo "📊 Performance: ";
        echo "โหลดข้อมูล: " . number_format($load_time * 1000, 2) . "ms | ";
        echo "ค้นหา: " . number_format($search_time * 1000, 2) . "ms | ";
        echo "รวม: " . number_format($total_time * 1000, 2) . "ms | ";
        echo "จำนวนพนักงาน: " . number_format(count($employee_data)) . " คน";
        
        // ตรวจสอบว่าใช้ cache อะไร
        if (function_exists('apcu_fetch') && apcu_fetch('employee_data_map') !== false) {
            echo " | ใช้ APCu Cache ✅";
        } elseif (file_exists(__DIR__ . '/cache/employee_cache.php')) {
            echo " | ใช้ File Cache 📁";
        } else {
            echo " | อ่านจาก CSV 📄";
        }
        echo '</div>';
    }
    
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
            <div class="ui relaxed divided list">
                <div class="item">
                    <div class="header">รหัสพนักงาน</div>
                    <?= htmlspecialchars($row['emp_id']) ?>
                </div>
                <div class="item">
                    <div class="header">ชื่อ</div>
                    <?= htmlspecialchars($row['emp_name']) ?>
                </div>
                <div class="item">
                    <div class="header">ตำแหน่ง</div>
                    <?= htmlspecialchars($row['position'] ?? 'ไม่ระบุ') ?>
                </div>
                <div class="item">
                    <div class="header">ส่วนงานย่อ</div>
                    <?= htmlspecialchars($row['sec_short'] ?? 'ไม่ระบุ') ?>
                </div>
                <div class="item">
                    <div class="header">ชื่อหน่วยงาน</div>
                    <?= htmlspecialchars($row['cc_name'] ?? 'ไม่ระบุ') ?>
                </div>
            </div>
        </div>
        <a href="index.php" class="ui primary button">กลับหน้าแรก</a>
<?php
        // --- END: ปรับปรุงการแสดงผลเมื่อสำเร็จ ---

        // ส่งข้อมูลไป Google Sheets (แบบ async เพื่อไม่ให้ user รอนาน)
        $url = "https://script.google.com/macros/s/AKfycbyQcNpLCgjbeVAfGZwmK9suB5OuWPyGl2W5UJ98tIqumUk2-Yu9w9a-UzhjTjhtvcM/exec";
        $data_to_send = [
            'รหัสพนักงาน' => $row['emp_id'], 
            'ชื่อ' => $row['emp_name'], 
            'ตำแหน่ง' => $row['position'],
            'ส่วนงานย่อ' => $row['sec_short'], 
            'ชื่อศูนย์ต้นทุน' => $row['cc_name']
        ];
        
        $options = [
            'http' => [
                'header'  => "Content-type: application/json\r\n",
                'method'  => 'POST',
                'content' => json_encode($data_to_send),
                'timeout' => 5 // timeout 5 วินาที เพื่อไม่ให้ user รอนาน
            ]
        ];
        $context = stream_context_create($options);
        @file_get_contents($url, false, $context); // ใช้ @ เพื่อไม่แสดง error ถ้า Google Sheets down
    
    } else {
        // --- START: ปรับปรุงการแสดงผลเมื่อไม่สำเร็จ ---
?>
        <div class="ui segment">
            <div class="ui icon negative message">
                <i class="times circle outline icon"></i>
                <div class="content">
                    <div class="header">รหัสไม่ถูกต้องหรือไม่พบข้อมูล</div>
                    <p>กรุณาตรวจสอบรหัสพนักงาน หรือกรอกข้อมูลด้วยตนเองด้านล่าง</p>
                    <p><small>รหัสที่ค้นหา: "<?= htmlspecialchars($emp_id) ?>"</small></p>
                </div>
            </div>

            <h3 class="ui dividing header">กรอกข้อมูลด้วยตนเอง</h3>
            
            <form class="ui form" name="addform" method="POST" action="register_manual.php">
                <div class="field">
                    <label>รหัสพนักงาน <span style="color: gray;">(ไม่ต้องใส่ 0 ด้านหน้า)</span></label>
                    <input type="text" name="new_emp_id" value="<?= htmlspecialchars($emp_id) ?>" required>
                </div>
                <div class="field">
                    <label>ชื่อ-นามสกุล</label>
                    <input type="text" name="new_emp_name" required>
                </div>
                <div class="field">
                    <label>ตำแหน่ง <span style="color: gray;">(optional)</span></label>
                    <input type="text" name="new_position">
                </div>
                <div class="field">
                    <label>ส่วนงานย่อ <span style="color: gray;">(optional)</span></label>
                    <input type="text" name="new_sec_short">
                </div>
                <div class="field">
                    <label>ชื่อหน่วยงาน <span style="color: gray;">(optional)</span></label>
                    <input type="text" name="new_cc_name">
                </div>
                <button class="ui primary button" type="submit">ลงทะเบียน</button>
                <div class="ui button" onclick="window.history.back()">ย้อนกลับ</div>
            </form>
        </div>
<?php
        // --- END: ปรับปรุงการแสดงผลเมื่อไม่สำเร็จ ---
    }
} catch (Exception $e) {
    echo '<div class="ui error icon message"><i class="exclamation triangle icon"></i><div class="content"><div class="header">เกิดข้อผิดพลาด</div><p>' . htmlspecialchars($e->getMessage()) . '</p></div></div>';
}
?>
</div>
</body>
</html>
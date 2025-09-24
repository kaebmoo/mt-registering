<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>แบบฟอร์มลงทะเบียนการประชุม</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body class="ui container" style="margin-top: 40px;">
    
    <?php
    // อ่านข้อมูลการประชุมจากไฟล์ schedule.json
    $schedule_file = __DIR__ . '/schedule.json';
    if (file_exists($schedule_file)) {
        $json_data = file_get_contents($schedule_file);
        $head = json_decode($json_data, true); // true เพื่อให้เป็น associative array

        if ($head) {
            echo '<div class="ui raised blue segment">';
            echo "<h2 class='ui header'>หัวข้อการประชุม: " . htmlspecialchars($head["topic"]) . "</h2>";
            echo "<p><strong>วันที่:</strong> " . htmlspecialchars($head["date"]) . 
                 " <strong>เวลา:</strong> " . htmlspecialchars($head["start_time"]) . 
                 " - " . htmlspecialchars($head["end_time"]). "</p>";
            echo "<p><strong>สถานที่:</strong> ห้องประชุม " . htmlspecialchars($head["room"]) . 
                 " ชั้น " . htmlspecialchars($head["floor"]) . 
                 " อาคาร " . htmlspecialchars($head["building"]) . "</p>";
            echo '</div>';
        }
    } else {
        echo "<div class='ui message warning'>ไม่พบข้อมูลการประชุม (schedule.json)</div>";
    }
    ?>
    
    <form class="ui form" name="mainform" method="POST" action="register.php">
        <div class="field">
            รหัสพนักงาน <span style="color: gray;"> (ไม่ต้องใส่ 0 ด้านหน้า)</span> 
            <input type="text" name="emp_id"/>
        </div>
        <button class="ui primary button" type="submit">ลงทะเบียน</button>	
        <br>
     </form>
    
</body>
</html>

<?php
// apcu_status.php
// หน้าสำหรับตรวจสอบสถานะของ APCu Cache
?>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>APCu Cache Status</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { padding: 40px; background-color: #f9f9f9; }
        .ui.table th { background-color: #f0f0f0; }
    </style>
</head>
<body>
<div class="ui container">
    <h2 class="ui dividing header">
        <i class="database icon"></i>
        <div class="content">
            APCu Cache Status
            <div class="sub header">ข้อมูลสถานะของแคชในหน่วยความจำ</div>
        </div>
    </h2>

    <?php if (function_exists('apcu_fetch')): ?>
        
        <div class="ui icon positive message">
            <i class="check circle icon"></i>
            <div class="content">
                <div class="header">APCu is Enabled</div>
                <p>ส่วนเสริม APCu ถูกเปิดใช้งานบนเซิร์ฟเวอร์นี้</p>
            </div>
        </div>

        <?php
            $cache_key = 'employee_data_map';
            $info = apcu_cache_info();
            $mem = apcu_sma_info();
            $cache_exists = apcu_exists($cache_key);
        ?>

        <div class="ui segment">
            <h3 class="ui header">สถานะแคชข้อมูลพนักงาน (Key: <?= $cache_key ?>)</h3>
            <?php if ($cache_exists): ?>
                <div class="ui green label">
                    <i class="archive icon"></i> In Cache
                    <div class="detail">มีข้อมูลพนักงานอยู่ในแคช</div>
                </div>
                <p style="margin-top: 10px;">ข้อมูลพนักงานถูกอ่านจากไฟล์ CSV และเก็บไว้ในหน่วยความจำแล้ว การลงทะเบียนครั้งต่อไปจะดึงข้อมูลจากที่นี่</p>
            <?php else: ?>
                <div class="ui yellow label">
                    <i class="file outline icon"></i> Not In Cache
                    <div class="detail">ยังไม่มีข้อมูลพนักงานในแคช</div>
                </div>
                <p style="margin-top: 10px;">การลงทะเบียนครั้งแรกจะทำการอ่านไฟล์ CSV และนำข้อมูลมาเก็บในแคช</p>
            <?php endif; ?>
            <a href="clear_cache.php" class="ui red button" style="margin-top: 15px;"><i class="trash icon"></i> ล้างแคชทั้งหมด</a>
        </div>

        <div class="ui segment">
            <h3 class="ui header">สถิติการใช้งาน</h3>
            <table class="ui celled table">
                <tbody>
                    <tr>
                        <td><strong>จำนวนครั้งที่เรียกใช้แคช (Hits)</strong></td>
                        <td><?= number_format($info['num_hits']) ?></td>
                    </tr>
                    <tr>
                        <td><strong>จำนวนครั้งที่หาไม่เจอ (Misses)</strong></td>
                        <td><?= number_format($info['num_misses']) ?></td>
                    </tr>
                    <tr>
                        <td><strong>อัตราส่วน Hit / Miss</strong></td>
                        <td><?= round($info['num_hits'] / ($info['num_hits'] + $info['num_misses'] + 1) * 100, 2) ?>%</td>
                    </tr>
                    <tr>
                        <td><strong>เวลาเริ่มต้นแคช</strong></td>
                        <td><?= date('Y-m-d H:i:s', $info['start_time']) ?></td>
                    </tr>
                </tbody>
            </table>
        </div>

    <?php else: ?>
        <div class="ui icon negative message">
            <i class="times circle icon"></i>
            <div class="content">
                <div class="header">APCu is Not Enabled</div>
                <p>ส่วนเสริม APCu ไม่ได้ถูกเปิดใช้งาน แอปพลิเคชันจะอ่านไฟล์ CSV ทุกครั้ง</p>
            </div>
        </div>
    <?php endif; ?>

</div>
</body>
</html>

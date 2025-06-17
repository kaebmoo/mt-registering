<html>
<body>
<?php 
	$emp_id = $_POST['emp_id'];

    try {
        // เชื่อมต่อกับไฟล์ SQLite ชื่อ employee.db
        $db = new PDO('sqlite:employee.db');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // เตรียมคำสั่ง SQL แบบปลอดภัย (Prepared Statement)
        $stmt = $db->prepare("SELECT emp_name, department, position FROM employee WHERE emp_id = :emp_id");
        $stmt->bindValue(':emp_id', $emp_id, PDO::PARAM_STR);
        $stmt->execute();

        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($row && strlen($emp_id) === 6) {
            echo "<h2>ลงทะเบียนสำเร็จ</h2>";
            echo "ชื่อ: " . htmlspecialchars($row['emp_name']) . "<br>";
            echo "แผนก: " . htmlspecialchars($row['department']) . "<br>";
            echo "ตำแหน่ง: " . htmlspecialchars($row['position']) . "<br>";
		
	    $url = "https://script.google.com/macros/s/AKfycbxpaqzlOWrsq6GmmZkh8RUnQBwOddtnqNAwsY6C87Rrull0ZCcgRgkHIyRW1JuOQLh7/exec";
	    $data = array(
                'รหัสพนักงาน' => $emp_id,
                'ชื่อ' => $row['emp_name'],
                'แผนก' => $row['department'],
                'ตำแหน่ง' => $row['position']
            );

            $options = array(
                'http' => array(
                    'header'  => "Content-type: application/json",
                    'method'  => 'POST',
                    'content' => json_encode($data),
                ),
            );

            $context = stream_context_create($options);
            $result = file_get_contents($url, false, $context);
		
        } else {
            echo "รหัสไม่ถูกต้องหรือไม่พบข้อมูล";
		
                echo '<div class="options-container">';
                echo '<button onclick="window.history.back()">ย้อนกลับ</button>'; // ปุ่มย้อนกลับ
                echo '</div>';

                echo '<div class="additional-form">';
                echo '<h3>กรอกข้อมูลด้วยตนเอง</h3>';
                ?>
                <form name="mainform" method="POST" action="register.php">
        		รหัสพนักงาน: <input type="text" name="new_emp_id" value="" size="10" /> <br>
			ชื่อ-นามสกุล: <input type="text" name="new_emp_name" value="" size="20" /> <br>
			แผนก: <input type="text" name="new_department" value="" size="20" /> <br>
			ตำแหน่ง: <input type="text" name="new_position" value="" size="20" /> <br>
        		<input type="submit" value="Submit"/>	
     		</form>
                <?php
                echo '</div>'; // close additional-form
            }
   	}
        }

    } catch (PDOException $e) {
        echo "เกิดข้อผิดพลาด: " . $e->getMessage();
    } 
?>
</body>
</html>

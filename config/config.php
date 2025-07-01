<?php
// config/config.php - Configuration Helper Class

class Config {
    private static $config = [];
    private static $loaded = false;
    
    /**
     * โหลด Environment Variables จากไฟล์ .env
     */
    public static function loadEnv($path = null) {
        if (self::$loaded) {
            return true;
        }
        
        $envPath = $path ?: dirname(__DIR__) . '/.env';
        
        if (!file_exists($envPath)) {
            // ถ้าไม่มีไฟล์ .env ให้ใช้ค่าจาก server environment
            self::$loaded = true;
            return false;
        }
        
        $lines = file($envPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        
        foreach ($lines as $line) {
            $line = trim($line);
            
            // ข้าม comment lines
            if (empty($line) || strpos($line, '#') === 0) {
                continue;
            }
            
            // แยก key=value
            if (strpos($line, '=') !== false) {
                list($key, $value) = explode('=', $line, 2);
                $key = trim($key);
                $value = trim($value, " \t\n\r\0\x0B\"'");
                
                // เก็บลง environment
                if (!array_key_exists($key, $_ENV)) {
                    putenv("$key=$value");
                    $_ENV[$key] = $value;
                    $_SERVER[$key] = $value;
                }
                
                // เก็บใน config array
                self::$config[$key] = $value;
            }
        }
        
        self::$loaded = true;
        return true;
    }
    
    /**
     * ดึงค่า configuration
     */
    public static function get($key, $default = null) {
        // โหลด env ถ้ายังไม่ได้โหลด
        if (!self::$loaded) {
            self::loadEnv();
        }
        
        // ลำดับการหาค่า: ENV -> SERVER -> Config Array -> Default
        $sources = [
            $_ENV[$key] ?? null,
            $_SERVER[$key] ?? null,
            getenv($key) ?: null,
            self::$config[$key] ?? null
        ];
        
        foreach ($sources as $value) {
            if ($value !== null && $value !== '') {
                // แปลงค่า boolean strings
                if (strtolower($value) === 'true') return true;
                if (strtolower($value) === 'false') return false;
                
                // แปลงค่า numeric
                if (is_numeric($value)) {
                    return strpos($value, '.') !== false ? (float)$value : (int)$value;
                }
                
                return $value;
            }
        }
        
        return $default;
    }
    
    /**
     * ตรวจสอบว่ามี key หรือไม่
     */
    public static function has($key) {
        return self::get($key) !== null;
    }
    
    /**
     * ดึงค่าทั้งหมด
     */
    public static function all() {
        if (!self::$loaded) {
            self::loadEnv();
        }
        return self::$config;
    }
    
    /**
     * ตรวจสอบว่าอยู่ในโหมด debug หรือไม่
     */
    public static function isDebug() {
        return self::get('DEBUG_MODE', false) === true;
    }
    
    /**
     * ดึง Google Script URL
     */
    public static function getGoogleScriptUrl() {
        $url = self::get('GOOGLE_SCRIPT_URL');
        
        if (empty($url)) {
            throw new Exception('Google Script URL ไม่ได้ตั้งค่าใน environment variables');
        }
        
        return $url;
    }
    
    /**
     * ดึงค่า timeout สำหรับ HTTP requests
     */
    public static function getTimeout() {
        return self::get('APP_TIMEOUT', 5);
    }
    
    /**
     * ดึงค่า cache TTL
     */
    public static function getCacheTTL() {
        return self::get('CACHE_TTL', 3600);
    }
    
    /**
     * ดึงการตั้งค่า database
     */
    public static function getDatabaseConfig() {
        return [
            'host' => self::get('DB_HOST', 'localhost'),
            'name' => self::get('DB_NAME', ''),
            'user' => self::get('DB_USER', ''),
            'password' => self::get('DB_PASSWORD', '')
        ];
    }
}

// โหลด environment variables ทันที
Config::loadEnv();
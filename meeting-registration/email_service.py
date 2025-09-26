# email_service.py - แก้ไข encoding issue
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    """Email service using SMTP SSL"""
    
    def __init__(self):
        self.smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.port = int(os.environ.get('MAIL_PORT', 465))  # SSL port
        self.sender_email = os.environ.get('MAIL_USERNAME')
        self.sender_password = os.environ.get('MAIL_PASSWORD')
        self.sender_name = os.environ.get('MAIL_FROM_NAME', 'Meeting Registration System')
        
    def send_otp_email(self, recipient_email: str, recipient_name: str, otp: str, purpose: str = 'login'):
        """Send OTP email with proper encoding"""
        try:
            # Create message with UTF-8 policy
            message = MIMEMultipart('alternative')
            
            # Email headers with proper encoding
            if purpose == 'register':
                subject = "ยืนยัน Email - ระบบลงทะเบียนการประชุม"
            else:
                subject = "เข้าสู่ระบบ - รหัส OTP"
            
            # ✅ Force UTF-8 encoding for headers
            message["Subject"] = Header(subject, 'utf-8')
            message["From"] = formataddr((
                Header(self.sender_name, 'utf-8').encode(),
                self.sender_email
            ))
            message["To"] = formataddr((
                Header(recipient_name or recipient_email, 'utf-8').encode(),
                recipient_email
            ))
            
            # Plain text version
            text_content = f"""
สวัสดี {recipient_name or 'คุณ'},

รหัส OTP ของคุณคือ: {otp}

รหัสนี้จะหมดอายุใน 10 นาที
กรุณาอย่าแชร์รหัสนี้กับผู้อื่น

ขอบคุณ,
ระบบลงทะเบียนการประชุม
            """
            
            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Sarabun', Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2185d0; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .otp-code {{ 
            font-size: 32px; 
            font-weight: bold; 
            color: #2185d0; 
            text-align: center; 
            padding: 20px;
            background-color: white;
            border: 2px dashed #2185d0;
            margin: 20px 0;
            letter-spacing: 5px;
            border-radius: 5px;
        }}
        .footer {{ text-align: center; padding: 10px; color: #666; font-size: 12px; }}
        .warning {{ color: #ff6b6b; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{'ยืนยัน Email' if purpose == 'register' else 'เข้าสู่ระบบ'}</h2>
        </div>
        <div class="content">
            <p>สวัสดี <strong>{recipient_name or 'คุณ'}</strong>,</p>
            <p>รหัส OTP ของคุณคือ:</p>
            <div class="otp-code">{otp}</div>
            <p>⏱️ <span class="warning">รหัสนี้จะหมดอายุใน 10 นาที</span></p>
            <p>🔒 กรุณาอย่าแชร์รหัสนี้กับผู้อื่น</p>
        </div>
        <div class="footer">
            <p>ขอบคุณที่ใช้บริการ<br>ระบบลงทะเบียนการประชุม</p>
            <p>อีเมลนี้ส่งถึง: {recipient_email}</p>
        </div>
    </div>
</body>
</html>
            """
            
            # ✅ Create MIME parts with explicit UTF-8 encoding
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            # Attach parts
            message.attach(part1)
            message.attach(part2)
            
            # ✅ Convert message to string with UTF-8
            message_string = message.as_string()
            
            # Send email via SSL
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                # ✅ Ensure UTF-8 encoding for server
                server.set_debuglevel(0)  # Set to 1 for debugging
                server.ehlo()
                server.login(self.sender_email, self.sender_password)
                
                # ✅ Send with proper encoding
                server.send_message(message)
                # Alternative: server.sendmail(self.sender_email, recipient_email, message_string.encode('utf-8'))
                
            logger.info(f"✅ OTP email sent to: {recipient_email}")
            return True
            
        except UnicodeEncodeError as e:
            logger.error(f"❌ Unicode encoding error for {recipient_email}: {str(e)}")
            return False
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error for {recipient_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send email to {recipient_email}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def test_connection(self):
        """Test SMTP connection"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.ehlo()
                server.login(self.sender_email, self.sender_password)
                logger.info("✅ SMTP connection successful")
                return True
        except Exception as e:
            logger.error(f"❌ SMTP connection failed: {str(e)}")
            return False
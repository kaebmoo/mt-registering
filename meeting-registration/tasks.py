# tasks.py
from rq import Queue
from redis import Redis
from email_service import EmailService
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import smtplib
import ssl
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_conn = Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
email_queue = Queue('email', connection=redis_conn)

def send_otp_email_task(recipient_email: str, recipient_name: str, otp: str, purpose: str = 'login'):
    """Background task to send OTP email"""
    email_service = EmailService()
    return email_service.send_otp_email(recipient_email, recipient_name, otp, purpose)

def send_registration_notification(registration_data: dict, meeting_data: dict):
    """Send registration confirmation email"""
    email_service = EmailService()
    
    message = MIMEMultipart()
    message["Subject"] = Header(f"ยืนยันการลงทะเบียน - {meeting_data['topic']}", 'utf-8')
    message["From"] = formataddr((email_service.sender_name, email_service.sender_email))
    message["To"] = registration_data.get('email', '')
    
    # Create confirmation email content
    html_content = f"""
    <html>
    <body style="font-family: 'Sarabun', Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2185d0;">✅ ลงทะเบียนสำเร็จ</h2>
            <p><strong>ชื่อ:</strong> {registration_data['emp_name']}</p>
            <p><strong>รหัสพนักงาน:</strong> {registration_data['emp_id']}</p>
            <hr>
            <h3>รายละเอียดการประชุม</h3>
            <p><strong>หัวข้อ:</strong> {meeting_data['topic']}</p>
            <p><strong>วันที่:</strong> {meeting_data['meeting_date']}</p>
            <p><strong>เวลา:</strong> {meeting_data['start_time']} - {meeting_data['end_time']}</p>
            <p><strong>สถานที่:</strong> ห้อง {meeting_data['room']} ชั้น {meeting_data['floor']}</p>
        </div>
    </body>
    </html>
    """
    
    message.attach(MIMEText(html_content, "html", "utf-8"))
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(email_service.smtp_server, email_service.port, context=context) as server:
            server.login(email_service.sender_email, email_service.sender_password)
            server.sendmail(email_service.sender_email, registration_data['email'], message.as_string())
        logger.info(f"✅ Registration confirmation sent to: {registration_data['email']}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send registration email: {str(e)}")
        return False
# This file is the entrypoint for the Celery worker.
from app import create_app
from extensions import celery_app

# สร้าง Flask app instance เพื่อให้ Celery task มี app context
# ตัว Celery จะไปดึง celery_app object ที่ถูกตั้งค่าแล้วจากใน app เอง
app = create_app()
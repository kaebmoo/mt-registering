from flask_caching import Cache
from celery import Celery

# สร้าง Celery instance โดยยังไม่ผูกกับ app
# เราจะกำหนดค่า broker และ backend ภายหลังใน create_app
celery_app = Celery(__name__)

# สร้าง Cache instance
cache = Cache()
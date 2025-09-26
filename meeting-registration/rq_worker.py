# rq_worker.py
import os
import sys
from rq import Worker
from redis import Redis

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Initialize Flask app context
app = create_app()
app.app_context().push()

# Setup Redis connection
redis_conn = Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))

if __name__ == '__main__':

    worker = Worker(['email', 'default'], connection=redis_conn) 
    worker.work()
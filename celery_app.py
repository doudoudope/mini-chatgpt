import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery = Celery(
    "mini_chatgpt",
    broker=f"{REDIS_URL}/0",
    backend=f"{REDIS_URL}/1",
    include=["tasks"],
)

celery.conf.update(result_expires=86400)  # job results kept for 24 hours

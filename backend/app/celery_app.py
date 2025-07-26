from celery import Celery
from .core.config import settings

# Create Celery instance
celery_app = Celery(
    "stock_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Add periodic tasks here if needed
    # 'update-stock-data': {
    #     'task': 'app.tasks.update_stock_data',
    #     'schedule': crontab(minute=0, hour='*/1'),  # Every hour
    # },
} 
from celery import Celery
from config import settings

# Create the Celery application instance
# The broker is the Redis instance where Celery sends task messages.
# The backend is also Redis, where Celery stores task states and results.
celery_app = Celery(
    "JobOrchestrator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["main"]  # List of modules to import when a worker starts. 'main' contains our tasks.
)

# Optional Celery configuration
celery_app.conf.update(
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

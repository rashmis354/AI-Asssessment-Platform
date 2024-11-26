from celery import Celery
from modules.utils.generate_log_file import logger

app = Celery(
    'Tasks',
    broker='redis://localhost:6379/0',  # Assuming Redis is running on localhost
    backend='redis://localhost:6379/0',  # Result backend
    include=["modules.tasks.celery_tasks"]  # Ensure this matches the name of your tasks module
)

if __name__ == "__main__":
    logger.info("Starting celery")
    app.start()

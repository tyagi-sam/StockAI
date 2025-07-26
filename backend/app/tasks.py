from .celery_app import celery_app
from .core.logger import logger

@celery_app.task
def example_task():
    """Example background task"""
    logger.info("Running example background task")
    return "Task completed successfully"

@celery_app.task
def update_stock_data():
    """Update stock data in background"""
    logger.info("Updating stock data")
    # Add your stock data update logic here
    return "Stock data updated" 
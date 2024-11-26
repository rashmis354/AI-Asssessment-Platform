import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from config.config import LOGS_FOLDER_NAME,LOG_FILE_BASE_NAME,file_rotation,file_rotation_interval,backupCount,default_log_level


log_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_dir = os.path.join(os.getcwd(), LOGS_FOLDER_NAME)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
app_log_file = os.path.join(log_dir, LOG_FILE_BASE_NAME.format(log_date=log_date))

handler = TimedRotatingFileHandler(app_log_file, when=file_rotation, interval=file_rotation_interval, backupCount=backupCount)
handler.suffix = "%Y%m%d%H%M%S"
handler.setFormatter(logging.Formatter("[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))

logger = logging.getLogger('app_logger')
logger.addHandler(handler)
logger.setLevel(default_log_level)

def delete_old_logs(log_directory, days=1):
    cutoff_time = datetime.now() - timedelta(days=days)
    for filename in os.listdir(log_directory):
        file_path = os.path.join(log_directory, filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if file_creation_time < cutoff_time:
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted old log file: {file_path}")
                except FileNotFoundError:
                    logger.warning(f"File not found: {file_path}")
                except Exception as e:
                    logger.exception(f"Error deleting file {file_path}: {e}")
                    
delete_old_logs(log_dir)
import logging
import os
import datetime  # ✅ To'liq import
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Log papkasini yaratish
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Joriy sana bilan log fayl nomi
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # ✅ datetime.datetime
    log_file = os.path.join(log_dir, f"bot_{current_date}.log")
    
    # Logger yaratish
    logger = logging.getLogger("bot")
    logger.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (max 5MB, 5 backup fayl)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Handlerlarni qo'shish
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Global logger
logger = setup_logger()
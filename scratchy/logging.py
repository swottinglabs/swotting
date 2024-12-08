import logging
from logging.handlers import RotatingFileHandler
import os
from io import StringIO
from django.conf import settings
from typing import Tuple, List

class SpiderExecutionLogger:
    def __init__(self, spider_name: str):
        self.spider_name = spider_name
        self.log_dir = self._ensure_log_directory()
        self.log_file_path = os.path.join(self.log_dir, f"{spider_name}.log")

    def _ensure_log_directory(self) -> str:
        """Ensure the log directory exists and return its path"""
        log_dir = getattr(settings, 'SCRATCHY_LOG_DIR', 'spider_logs')
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(settings.BASE_DIR, log_dir)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def setup_logging(self) -> Tuple[StringIO, List[logging.Handler]]:
        """Setup both memory and rotating file logging handlers"""
        # Memory handler for database storage
        log_capture_string = StringIO()
        string_handler = logging.StreamHandler(log_capture_string)
        
        # Rotating file handler for persistent logs
        file_handler = RotatingFileHandler(
            filename=self.log_file_path,
            maxBytes=5 * 1024 * 1024,  # 5MB per file
            backupCount=5,  # Keep 5 backup files
            encoding='utf-8'
        )
        
        # Create and apply formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        for handler in [string_handler, file_handler]:
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO)
        
        return log_capture_string, [string_handler, file_handler]

    def cleanup_logging(self, handlers: List[logging.Handler], logger: logging.Logger) -> None:
        """Clean up all logging handlers"""
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close() 
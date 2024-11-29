import logging
from io import StringIO

class SpiderExecutionLogger:
    def __init__(self, spider_name: str):
        self.spider_name = spider_name

    def setup_logging(self):
        log_capture_string = StringIO()
        log_handler = logging.StreamHandler(log_capture_string)
        log_handler.setLevel(logging.INFO)
        return log_capture_string, log_handler

    def cleanup_logging(self, handler, logger):
        logger.removeHandler(handler)
        handler.close() 
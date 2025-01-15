from abc import ABC, abstractmethod
from typing import Any, Dict
from scrapy.exceptions import DropItem
import logging

class BaseValidatorPipeline(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        pass

    def _handle_validation_error(self, error: Exception, item_type: str) -> None:
        error_msg = f"Invalid {item_type}: {str(error)}"
        self.logger.error(error_msg)
        raise DropItem(error_msg) 
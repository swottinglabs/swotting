from typing import Any, Dict
from .base_temp_save import BaseTempSavePipeline
import logging

class LearningResourceTempSavePipeline(BaseTempSavePipeline):
    """Pipeline to temporarily save learning resource data to JSON files"""
    
    @property
    def subfolder(self) -> str:
        return 'learning_resource_jsons'

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info("LearningResourceTempSavePipeline initialized")

    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        self.logger.info(f"Processing item: {item.get('type')}")
        if 'type' in item and item['type'] == 'learning_resource':
            self.logger.info("Saving learning resource")
            self._save_to_json(item)
        return item 
from typing import Any, Dict
from .base_temp_save import BaseTempSavePipeline

class CreatorTempSavePipeline(BaseTempSavePipeline):
    """Pipeline to temporarily save creator data to JSON files"""
    
    @property
    def subfolder(self) -> str:
        return 'creator_jsons'

    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        if 'type' in item and item['type'] == 'creator':
            self._save_to_json(item)
        return item 
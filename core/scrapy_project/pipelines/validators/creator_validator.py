from typing import Any, Dict
from ...validators import CreatorInput
from .base_validator import BaseValidatorPipeline

class CreatorValidatorPipeline(BaseValidatorPipeline):
    """Pipeline to validate creator data using CreatorInput model"""
    
    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        if 'type' not in item or item['type'] != 'creator':
            return item
            
        try:
            validated_creator = CreatorInput(**item['data'])
            item['data'] = validated_creator.model_dump()
            return item
        except Exception as e:
            self._handle_validation_error(e, "creator") 
from typing import Any, Dict
from ...validators import LearningResourceInput
from .base_validator import BaseValidatorPipeline

class PreProcessValidatorPipeline(BaseValidatorPipeline):
    """Pipeline to validate incoming learning resource data using LearningResourceInput model"""
    
    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        if 'type' not in item or item['type'] != 'learning_resource':
            return item
            
        try:
            validated_resource = LearningResourceInput(**item['data'])
            item['data'] = validated_resource.model_dump()
            return item
        except Exception as e:
            self._handle_validation_error(e, "learning resource") 
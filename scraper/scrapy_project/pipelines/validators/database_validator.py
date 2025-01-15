from typing import Any, Dict, List
from ...validators import LearningResourceOutput, CreatorOutput
from .base_validator import BaseValidatorPipeline
from uuid import uuid4

class DatabaseValidatorPipeline(BaseValidatorPipeline):
    """Pipeline to validate learning resource and creator data before database insertion"""
    
    def _validate_creators(self, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate creator data and assign UUIDs"""
        validated_creators = []
        
        for creator in creators:
            try:
                validated_creator = CreatorOutput(**creator)
                validated_creators.append(validated_creator.model_dump())
            except Exception as e:
                self._handle_validation_error(e, "creator")
        
        return validated_creators

    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        """Validate both learning resource and its creators before database insertion"""
        if 'type' not in item or item['type'] != 'learning_resource':
            return item
            
        try:
            # First validate creators and assign UUIDs
            if 'creators' in item['data']:
                item['data']['creators'] = self._validate_creators(item['data']['creators'])
            
            # Then validate the entire learning resource
            validated_resource = LearningResourceOutput(**item['data'])
            item['data'] = validated_resource.model_dump()
            
            return item
        except Exception as e:
            self._handle_validation_error(e, "learning resource database validation") 
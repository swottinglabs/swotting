import os
import json
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime
from decimal import Decimal
from pydantic import HttpUrl, AnyUrl

class BaseTempSavePipeline(ABC):
    """Base class for temporary JSON save pipelines"""
    
    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), 'data')
        self._ensure_directories()

    @property
    @abstractmethod
    def subfolder(self) -> str:
        """Return the subfolder name for this pipeline type"""
        pass

    def _ensure_directories(self) -> None:
        """Ensure the necessary directories exist"""
        save_path = os.path.join(self.base_path, self.subfolder)
        os.makedirs(save_path, exist_ok=True)

    def _generate_filename(self, item: Dict[str, Any]) -> str:
        """Generate a unique filename for the item"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return f"{timestamp}.json"

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for objects not serializable by default json code"""
        if hasattr(obj, '__str__') and 'Url' in obj.__class__.__name__:
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable')

    def _save_to_json(self, item: Dict[str, Any]) -> None:
        """Save the item to a JSON file"""
        filename = self._generate_filename(item)
        file_path = os.path.join(self.base_path, self.subfolder, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item['data'], f, 
                     default=self._json_serializer,
                     ensure_ascii=False, 
                     indent=2) 
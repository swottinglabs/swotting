import os
import json
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime

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

    def _save_to_json(self, item: Dict[str, Any]) -> None:
        """Save the item to a JSON file"""
        filename = self._generate_filename(item)
        file_path = os.path.join(self.base_path, self.subfolder, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item['data'], f, ensure_ascii=False, indent=2) 
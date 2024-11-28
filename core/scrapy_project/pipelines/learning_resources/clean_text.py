import re
from bs4 import BeautifulSoup
from typing import Any, Dict, Optional

class TextCleanerPipeline:
    """Pipeline to clean text fields in learning resources by removing HTML tags and special characters."""
    
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean text by removing HTML tags and normalizing whitespace.
        
        Args:
            text: String that may contain HTML tags and special characters
            
        Returns:
            Cleaned string with HTML removed and whitespace normalized
        """
        if not text:
            return text
            
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        # Replace HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        return text.strip()
    
    def _clean_creator(self, creator: Dict[str, Any]) -> Dict[str, Any]:
        """Clean text fields in a creator dictionary."""
        if not creator:
            return creator
            
        creator['name'] = self._clean_text(creator.get('name'))
        creator['description'] = self._clean_text(creator.get('description'))
        return creator
    
    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        """
        Process item by cleaning text fields.
        
        Args:
            item: Dictionary containing learning resource data
            spider: Spider instance that generated this item
            
        Returns:
            Cleaned item dictionary
        """
        if item.get('type') != 'learning_resource':
            return item
            
        data = item['data']
        
        # Clean main text fields
        data['name'] = self._clean_text(data.get('name'))
        data['description'] = self._clean_text(data.get('description'))
        data['short_description'] = self._clean_text(data.get('short_description'))
        
        # Clean creator text fields
        if 'creators' in data:
            data['creators'] = [
                self._clean_creator(creator) 
                for creator in data['creators']
            ]
            
        return item

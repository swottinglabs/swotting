from scrapy.exporters import JsonLinesItemExporter
from django.core.serializers.json import DjangoJSONEncoder
from urllib.parse import urlparse

class JsonLinesItemExporter(JsonLinesItemExporter):
    """Custom JSON Lines exporter that handles Django-specific types"""
    
    def __init__(self, file, **kwargs):
        # Use Django's JSON encoder by default
        kwargs['encoding'] = 'utf-8'
        kwargs['ensure_ascii'] = False
        super().__init__(file, **kwargs)
    
    def _serialize_value(self, value):
        """Handle special types before JSON serialization"""
        # Handle URL objects
        if hasattr(value, 'url'):
            return str(value.url)
        # Handle other URL-like objects
        if hasattr(value, '__str__'):
            try:
                parsed = urlparse(str(value))
                if parsed.scheme and parsed.netloc:
                    return str(value)
            except Exception:
                pass
        return super()._serialize_value(value)
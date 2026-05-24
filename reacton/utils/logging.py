"""
JSON-structured industrial logging utilities.
"""

import json
import time
from typing import Dict, Any

class StructuredLogger:
    """
    Industrial-grade JSON-structured event logger for SCADA and API tracking.
    """
    
    def __init__(self, component_name: str):
        self.component = component_name
        
    def _log(self, level: str, message: str, extra: Dict[str, Any] = None):
        """Format and print log message in JSON format."""
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level,
            "component": self.component,
            "message": message
        }
        if extra:
            payload["details"] = extra
        print(json.dumps(payload))
        
    def info(self, message: str, extra: Dict[str, Any] = None):
        self._log("INFO", message, extra)
        
    def warning(self, message: str, extra: Dict[str, Any] = None):
        self._log("WARNING", message, extra)
        
    def error(self, message: str, extra: Dict[str, Any] = None):
        self._log("ERROR", message, extra)
        
    def critical(self, message: str, extra: Dict[str, Any] = None):
        self._log("CRITICAL", message, extra)

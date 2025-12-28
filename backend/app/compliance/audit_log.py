"""
In-memory audit log (demo implementation)
Production would use database
"""

from typing import List, Dict
from datetime import datetime


class AuditLog:
    """Simple in-memory audit log."""
    
    def __init__(self):
        self._logs: List[Dict] = []
    
    def add_entry(self, entry: Dict) -> None:
        """Add new audit entry."""
        entry = dict(entry)
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
        self._logs.append(entry)
    
    def list_entries(self) -> List[Dict]:
        """Return all audit entries."""
        return list(self._logs)


# Global audit log instance
audit_log = AuditLog()

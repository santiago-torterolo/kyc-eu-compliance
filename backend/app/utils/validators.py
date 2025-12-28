"""
Input validation helpers
"""

from typing import List


def allowed_file(filename: str, allowed_extensions: List[str]) -> bool:
    """Return True if filename has allowed extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions

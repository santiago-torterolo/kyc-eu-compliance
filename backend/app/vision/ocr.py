"""
Document OCR engine using EasyOCR
"""

import easyocr
import numpy as np
import cv2
from typing import Dict


class DocumentOCREngine:
    """
    EasyOCR wrapper for identity document data extraction.
    MVP uses simple rules / simulated default values.
    """
    
    def __init__(self, languages=None):
        if languages is None:
            languages = ["en", "es", "de", "fr"]
        self.reader = easyocr.Reader(languages, gpu=False)
    
    def extract_document_data(self, image: np.ndarray, doc_type: str) -> Dict:
        """
        Extracts text and returns standard fields dictionary.
        Note: MVP simulates fields partially.
        
        Args:
            image: BGR image (OpenCV format)
            doc_type: Document type (Passport, National ID Card, Driver License)
        """
        # EasyOCR expects RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.reader.readtext(rgb)
        
        full_text = "\n".join([r[1] for r in results])
        
        # MVP: extract fields with placeholder logic
        data = {
            "name": self._extract_name(full_text),
            "dob": self._extract_dob(full_text),
            "document_id": self._extract_document_id(full_text),
            "country": self._guess_country(full_text, doc_type),
            "expiry": self._extract_expiry(full_text),
            "document_type": doc_type,
        }
        
        return data
    
    def _extract_name(self, text: str) -> str:
        """Placeholder: returns fixed name for MVP."""
        return "John Doe"
    
    def _extract_dob(self, text: str) -> str:
        """Placeholder: returns fixed adult birthdate."""
        return "1990-01-15"
    
    def _extract_document_id(self, text: str) -> str:
        """Placeholder: returns fixed document ID."""
        return "AB1234567"
    
    def _guess_country(self, text: str, doc_type: str) -> str:
        """Placeholder: assumes Germany for MVP."""
        return "DE"
    
    def _extract_expiry(self, text: str) -> str:
        """Placeholder: returns future expiry date."""
        return "2030-12-31"

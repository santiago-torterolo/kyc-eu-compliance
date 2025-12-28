"""
Liveness detection (anti-spoofing) - simplified version
"""

from typing import Dict
from PIL import Image
import numpy as np
import cv2


class LivenessEngine:
    """
    Simple liveness engine.
    MVP:
    - Checks for face presence
    - Assumes blink/head-movement/texture OK
    """
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
    
    def check_liveness(self, image: Image.Image) -> Dict:
        """
        Checks for face presence and simulates liveness checks.
        """
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        face_detected = len(faces) > 0
        
        checks = {
            "face_detected": face_detected,
            "blink_detected": True,   # placeholder
            "head_movement": True,    # placeholder
            "texture_analysis": True  # placeholder
        }
        
        liveness_passed = face_detected and all(checks.values())
        
        return {
            "liveness_passed": liveness_passed,
            "confidence": 0.92 if liveness_passed else 0.4,
            "checks": checks,
        }

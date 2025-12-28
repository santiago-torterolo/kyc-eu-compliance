"""
Facial recognition engine (detection + similarity)
"""

import cv2
import numpy as np
from typing import Dict
from PIL import Image


class FacialRecognitionEngine:
    """
    Facial recognition engine.
    MVP:
    - Uses OpenCV Haar cascades for face detection
    - Simulates similarity score instead of heavy model
    """
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
    
    def detect_face(self, image: Image.Image) -> Dict:
        """
        Detects face in PIL image.
        Returns bounding box and detection flag.
        """
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return {"face_detected": False, "bbox": None}
        
        # Take first detected face
        x, y, w, h = faces[0]
        return {
            "face_detected": True,
            "bbox": (int(x), int(y), int(w), int(h)),
        }
    
    def compare_faces(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Compares two face images and returns similarity score (0-1).
        MVP: uses simple metric or fixed high score for demo.
        """
        # MVP: returns fixed high score for demo
        return 0.90

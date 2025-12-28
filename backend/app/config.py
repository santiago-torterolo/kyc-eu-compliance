"""
Configuration management for KYC application
Loads environment variables and provides app settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_url: str = "http://localhost:8000"
    
    # Frontend Configuration
    frontend_url: str = "http://localhost:8501"
    allowed_origins: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://127.0.0.1:8501"
    ]
    
    # Security
    secret_key: str = "change-this-in-production"
    
    # OCR Configuration
    ocr_languages: List[str] = ["en", "es", "de", "fr"]
    ocr_gpu: bool = False
    
    # Face Recognition Configuration
    face_confidence_threshold: float = 0.85
    liveness_confidence_threshold: float = 0.75
    
    # Compliance Configuration
    minimum_age: int = 18
    document_max_age_years: int = 10
    
    # Data Retention
    audit_log_retention_days: int = 1825  # 5 years
    
    # File Upload
    max_upload_size_mb: int = 10
    allowed_extensions: List[str] = ["jpg", "jpeg", "png"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

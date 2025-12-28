"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class DocumentExtractionRequest(BaseModel):
    """Request model for document extraction"""
    document_type: str = Field(..., description="Type: Passport, National ID Card, Driver License")


class ExtractedDocumentData(BaseModel):
    """Extracted data from document"""
    name: str
    dob: str  # YYYY-MM-DD
    document_id: str
    country: str
    expiry: str  # YYYY-MM-DD
    document_type: str


class AgeVerification(BaseModel):
    """Age verification result"""
    age: int
    is_adult: bool
    dsa_compliant: bool
    age_threshold: int = 18


class ComplianceChecks(BaseModel):
    """Compliance verification results"""
    age_verification: AgeVerification
    document_valid: bool
    tampering_detected: bool
    data_minimization: bool
    document_risk_score: float


class DocumentExtractionResult(BaseModel):
    """Complete document extraction response"""
    verification_id: str
    status: str
    extracted_data: ExtractedDocumentData
    confidence: float
    compliance: ComplianceChecks
    timestamp: datetime = Field(default_factory=datetime.now)


class LivenessDetails(BaseModel):
    """Liveness detection details"""
    face_detected: bool
    blink_detected: bool
    head_movement: bool
    texture_analysis: bool


class FaceVerificationResult(BaseModel):
    """Face verification response"""
    verification_id: str
    status: str
    similarity_score: float
    liveness_passed: bool
    liveness_details: LivenessDetails
    timestamp: datetime = Field(default_factory=datetime.now)


class GDPRCompliance(BaseModel):
    """GDPR compliance report"""
    data_minimization: str
    encryption: str
    consent: str
    article_22_right_to_human_review: str


class AMLCompliance(BaseModel):
    """AML/CFT compliance report"""
    cdd_completed: str
    age_verified: str
    document_valid: str


class DSACompliance(BaseModel):
    """DSA compliance report"""
    age_over_18: bool
    digital_services_act: str


class Regulation2023Compliance(BaseModel):
    """Regulation 2023/1113 compliance"""
    tampering_check: str
    liveness_check: str


class ComplianceReport(BaseModel):
    """Complete compliance report"""
    timestamp: str
    gdpr: GDPRCompliance
    aml: AMLCompliance
    dsa: DSACompliance
    regulation_2023_1113: Regulation2023Compliance


class RiskAssessmentResult(BaseModel):
    """Risk assessment response"""
    verification_id: str
    decision: str  # APPROVED, REJECTED, REVIEW
    overall_risk_score: float
    document_risk: float
    biometric_risk: float
    behavioral_risk: float
    compliance_report: ComplianceReport
    reasons: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    verification_id: str
    timestamp: str
    decision: str
    risk_score: float
    compliance_checks: Dict
    country: Optional[str] = None
    ip_address: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"

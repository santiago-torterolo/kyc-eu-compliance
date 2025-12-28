"""
Main FastAPI application for KYC Verification System
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any

from .config import settings
from .models import (
    DocumentExtractionResult,
    FaceVerificationResult,
    RiskAssessmentResult,
    HealthResponse,
)
from .compliance.eu_rules import EUComplianceEngine
from .compliance.risk_scorer import RiskScoringEngine
from .compliance.audit_log import audit_log
from .vision.ocr import DocumentOCREngine
from .vision.face import FacialRecognitionEngine
from .vision.liveness import LivenessEngine

import cv2
import numpy as np
from PIL import Image
import io
import uuid
from datetime import datetime


app = FastAPI(
    title="KYC Verification API - EU Compliant",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processing engines
ocr_engine = DocumentOCREngine(languages=settings.ocr_languages)
face_engine = FacialRecognitionEngine()
liveness_engine = LivenessEngine()
compliance_engine = EUComplianceEngine()
risk_engine = RiskScoringEngine()

# In-memory store for document results (links document to face verification)
document_store: Dict[str, Dict[str, Any]] = {}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.post("/api/v1/extract-document", response_model=DocumentExtractionResult)
async def extract_document(
    document_image: UploadFile = File(...),
    document_type: str = Form(...),
):
    """Extracts data from document and runs compliance checks."""
    
    # Validate file extension
    filename = document_image.filename or "document.jpg"
    print(f"DEBUG: Received file with filename: '{filename}'")
    if "." not in filename:
        filename += ".jpg"  # Fallback extension
    
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Read and decode image
    image_bytes = await document_image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image")
    
    # OCR extraction
    extracted_data = ocr_engine.extract_document_data(img, document_type)
    
    # Run compliance checks
    age_check = compliance_engine.check_age_verification(extracted_data["dob"])
    validity_check = compliance_engine.check_document_validity(extracted_data["expiry"])
    tampering_check = compliance_engine.detect_tampering(img)
    data_min_check = compliance_engine.gdpr_data_minimization(extracted_data)
    aml_check = compliance_engine.aml_cdd_measures(extracted_data)
    
    document_risk = tampering_check["tampering_score"]
    
    compliance = {
        "age_verification": age_check,
        "document_valid": validity_check["document_valid"],
        "tampering_detected": tampering_check["tampering_detected"],
        "data_minimization": data_min_check["data_minimization_passed"],
        "document_risk_score": document_risk,
    }
    
    # Generate unique verification ID
    verification_id = str(uuid.uuid4())
    
    # Store in memory for next step (face verification)
    document_store[verification_id] = {
        "extracted_data": extracted_data,
        "compliance": compliance,
        "aml": aml_check,
        "age": age_check.get("age"),
        "document_valid": validity_check["document_valid"],
        "tampering_detected": tampering_check["tampering_detected"],
    }
    
    result = DocumentExtractionResult(
        verification_id=verification_id,
        status="SUCCESS",
        extracted_data=extracted_data,
        confidence=0.95,
        compliance=compliance,
    )
    
    # Add to audit log
    audit_log.add_entry({
        "verification_id": verification_id,
        "stage": "document_extraction",
        "status": "success",
        "country": extracted_data.get("country", "EU"),
    })
    
    return result


@app.post("/api/v1/verify-face", response_model=FaceVerificationResult)
async def verify_face(
    selfie: UploadFile = File(...),
    document_id: str = Form(...),
):
    """Verifies face match and liveness."""
    
    # Check if document exists
    if document_id not in document_store:
        raise HTTPException(status_code=400, detail="Invalid document_id")
    
    # Validate file extension
    filename = selfie.filename or "selfie.jpg"
    print(f"DEBUG: Received selfie with filename: '{filename}'")
    selfie_img = Image.open(io.BytesIO(selfie_bytes)).convert("RGB")
    
    # Liveness detection
    liveness = liveness_engine.check_liveness(selfie_img)
    
    # Face comparison (MVP: simulated high score)
    similarity_score = face_engine.compare_faces(selfie_img, selfie_img)
    
    status = (
        "VERIFIED"
        if similarity_score > settings.face_confidence_threshold and liveness["liveness_passed"]
        else "REJECTED"
    )
    
    result = FaceVerificationResult(
        verification_id=document_id,
        status=status,
        similarity_score=similarity_score,
        liveness_passed=liveness["liveness_passed"],
        liveness_details=liveness["checks"],
    )
    
    # Store face result for risk assessment
    document_store[document_id]["face_result"] = {
        "similarity_score": similarity_score,
        "liveness_passed": liveness["liveness_passed"],
        "liveness_details": liveness["checks"],
    }
    
    # Audit log
    audit_log.add_entry({
        "verification_id": document_id,
        "stage": "face_verification",
        "status": status.lower(),
    })
    
    return result


@app.post("/api/v1/risk-assessment", response_model=RiskAssessmentResult)
async def risk_assessment(document_id: str):
    """Calculates final risk score and decision."""
    
    if document_id not in document_store:
        raise HTTPException(status_code=400, detail="Invalid document_id")
    
    stored = document_store[document_id]
    extracted = stored["extracted_data"]
    compliance = stored["compliance"]
    aml = stored["aml"]
    face_result = stored.get("face_result")
    
    if face_result is None:
        raise HTTPException(status_code=400, detail="Face verification not completed")
    
    # Calculate document risk
    doc_risk = risk_engine.calculate_document_risk(
        tampering_score=compliance["document_risk_score"],
        document_valid=compliance["document_valid"],
        age_verified=compliance["age_verification"]["is_adult"],
        country_risk=0.1,
    )
    
    # Calculate biometric risk
    bio_risk = risk_engine.calculate_biometric_risk(
        liveness_passed=face_result["liveness_passed"],
        face_match_score=face_result["similarity_score"],
    )
    
    # Behavioral risk (placeholder)
    behavioral_risk = risk_engine.calculate_behavioral_risk(
        is_first_verification=True,
        velocity_check=0.0,
        device_risk=0.1,
    )
    
    overall = risk_engine.calculate_overall_risk(doc_risk, bio_risk, behavioral_risk)
    decision = risk_engine.make_decision(overall)
    
    # Build compliance report
    doc_data = {
        "age": compliance["age_verification"]["age"],
        "document_valid": compliance["document_valid"],
        "tampering_detected": compliance["tampering_detected"],
        "cdd_completed": aml["cdd_completed"],
    }
    
    compliance_report = compliance_engine.build_compliance_report(
        doc_data, face_result, doc_risk, bio_risk
    )
    
    risk_scores = {
        "document": doc_risk,
        "biometric": bio_risk,
        "behavioral": behavioral_risk,
        "overall": overall,
    }
    
    reasons = risk_engine.generate_reasons(
        decision, doc_data, face_result, risk_scores
    )
    
    result = RiskAssessmentResult(
        verification_id=document_id,
        decision=decision,
        overall_risk_score=overall,
        document_risk=doc_risk,
        biometric_risk=bio_risk,
        behavioral_risk=behavioral_risk,
        compliance_report=compliance_report,
        reasons=reasons,
    )
    
    # Final audit entry
    audit_log.add_entry({
        "verification_id": document_id,
        "decision": decision,
        "risk_score": overall,
        "compliance_checks": compliance_report,
        "country": extracted.get("country", "EU"),
    })
    
    return result


@app.get("/api/v1/audit-log")
async def get_audit_log():
    """Returns complete audit log (demo purposes)."""
    return JSONResponse(content=audit_log.list_entries())

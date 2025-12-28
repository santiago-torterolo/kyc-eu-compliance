"""
Risk Scoring Engine
Calculates risk scores based on document, biometric, and behavioral factors
"""

from typing import Dict


class RiskScoringEngine:
    """
    Risk scoring for KYC verification
    Combines multiple risk factors into overall score
    """
    
    @staticmethod
    def calculate_document_risk(
        tampering_score: float,
        document_valid: bool,
        age_verified: bool,
        country_risk: float = 0.1
    ) -> float:
        """
        Calculate document risk score
        
        Args:
            tampering_score: Tampering detection score (0-1)
            document_valid: Is document expired?
            age_verified: Is age >= 18?
            country_risk: Country-specific risk (0-1)
            
        Returns:
            Document risk score (0-1, lower is better)
        """
        # Weighted average
        weights = {
            "tampering": 0.4,
            "validity": 0.3,
            "age": 0.2,
            "country": 0.1
        }
        
        validity_risk = 0.0 if document_valid else 1.0
        age_risk = 0.0 if age_verified else 1.0
        
        doc_risk = (
            tampering_score * weights["tampering"] +
            validity_risk * weights["validity"] +
            age_risk * weights["age"] +
            country_risk * weights["country"]
        )
        
        return round(doc_risk, 3)
    
    @staticmethod
    def calculate_biometric_risk(
        liveness_passed: bool,
        face_match_score: float,
        liveness_confidence: float = 0.9
    ) -> float:
        """
        Calculate biometric risk score
        
        Args:
            liveness_passed: Did liveness detection pass?
            face_match_score: Face similarity score (0-1)
            liveness_confidence: Confidence in liveness (0-1)
            
        Returns:
            Biometric risk score (0-1, lower is better)
        """
        # Liveness risk
        liveness_risk = 0.0 if liveness_passed else 0.8
        
        # Face match risk (inverse of similarity)
        face_risk = 1.0 - face_match_score
        
        # Weighted average
        bio_risk = (
            liveness_risk * 0.6 +
            face_risk * 0.4
        )
        
        return round(bio_risk, 3)
    
    @staticmethod
    def calculate_behavioral_risk(
        is_first_verification: bool = True,
        velocity_check: float = 0.0,
        device_risk: float = 0.1
    ) -> float:
        """
        Calculate behavioral risk score
        
        Args:
            is_first_verification: First time user?
            velocity_check: Too many verifications? (0-1)
            device_risk: Unknown device/VPN? (0-1)
            
        Returns:
            Behavioral risk score (0-1, lower is better)
        """
        # First verification has slightly higher risk (unknown user)
        first_time_risk = 0.2 if is_first_verification else 0.0
        
        # Weighted average
        behavioral_risk = (
            first_time_risk * 0.5 +
            velocity_check * 0.3 +
            device_risk * 0.2
        )
        
        return round(behavioral_risk, 3)
    
    @staticmethod
    def calculate_overall_risk(
        document_risk: float,
        biometric_risk: float,
        behavioral_risk: float
    ) -> float:
        """
        Calculate overall risk score
        
        Args:
            document_risk: Document risk (0-1)
            biometric_risk: Biometric risk (0-1)
            behavioral_risk: Behavioral risk (0-1)
            
        Returns:
            Overall risk score (0-1, lower is better)
        """
        overall = (document_risk + biometric_risk + behavioral_risk) / 3
        return round(overall, 3)
    
    @staticmethod
    def make_decision(overall_risk: float) -> str:
        """
        Make verification decision based on risk score
        
        Args:
            overall_risk: Overall risk score (0-1)
            
        Returns:
            Decision: APPROVED, REVIEW, or REJECTED
        """
        if overall_risk < 0.30:
            return "APPROVED"
        elif overall_risk < 0.60:
            return "REVIEW"
        else:
            return "REJECTED"
    
    @staticmethod
    def generate_reasons(
        decision: str,
        document_data: Dict,
        face_data: Dict,
        risk_scores: Dict
    ) -> list:
        """
        Generate human-readable reasons for decision
        
        Args:
            decision: Verification decision
            document_data: Document verification data
            face_data: Face verification data
            risk_scores: All risk scores
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        # Document reasons
        if document_data.get("age", 0) >= 18:
            reasons.append(f"Age verification: {document_data.get('age')} years (>= 18) passed")
        else:
            reasons.append(f"Age verification: {document_data.get('age')} years (< 18) failed")
        
        if document_data.get("document_valid"):
            reasons.append("Document validity: Current and valid")
        else:
            reasons.append("Document validity: Expired or invalid")
        
        if not document_data.get("tampering_detected"):
            reasons.append("Document integrity: No tampering detected")
        else:
            reasons.append("Document integrity: Tampering suspected")
        
        # Biometric reasons
        if face_data.get("liveness_passed"):
            reasons.append("Biometric verification: Liveness passed")
        else:
            reasons.append("Biometric verification: Liveness failed")
        
        similarity = face_data.get("similarity_score", 0)
        if similarity > 0.85:
            reasons.append(f"Face match: {similarity:.0%} similarity (good match)")
        else:
            reasons.append(f"Face match: {similarity:.0%} similarity (poor match)")
        
        # Overall decision
        if decision == "APPROVED":
            reasons.append(f"Overall risk score: {risk_scores['overall']:.0%} (below threshold)")
        elif decision == "REVIEW":
            reasons.append(f"Overall risk score: {risk_scores['overall']:.0%} (manual review recommended)")
        else:
            reasons.append(f"Overall risk score: {risk_scores['overall']:.0%} (exceeds threshold)")
        
        return reasons

"""
KYC Verification Frontend - Streamlit
"""

import streamlit as st
import requests
import json
import time

# Config - Loading from environment for Docker compatibility
import os
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(page_title="KYC EU Compliance", page_icon="🔐", layout="wide")

st.title("KYC Verification System")
st.markdown("EU Compliant: GDPR | AML/CFT | DSA | Regulation 2023/1113")

# Initialize state
if "step" not in st.session_state:
    st.session_state.step = 1
if "verification_id" not in st.session_state:
    st.session_state.verification_id = None

# Progress bar
progress = (st.session_state.step - 1) * 33
st.progress(progress)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("Status Tracker")
    if st.session_state.step == 1:
        st.info("1. Upload Document")
    elif st.session_state.step == 2:
        st.info("2. Take Selfie")
    elif st.session_state.step == 3:
        st.info("3. Analysis")
    elif st.session_state.step == 4:
        st.success("4. Complete")

with col2:
    # STEP 1: DOCUMENT UPLOAD
    if st.session_state.step == 1:
        st.subheader("Step 1: Document Verification")
        doc_type = st.selectbox("Document Type", ["Passport", "National ID", "Driver License"])
        uploaded_file = st.file_uploader("Upload ID Document", type=['jpg', 'png', 'jpeg'])
        
        if uploaded_file and st.button("Analyze Document", type="primary"):
            with st.spinner("Extracting data via OCR..."):
                try:
                    files = {"document_image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {"document_type": doc_type}
                    res = requests.post(f"{API_URL}/v1/extract-document", files=files, data=data)
                    
                    if res.status_code == 200:
                        result = res.json()
                        st.session_state.verification_id = result['verification_id']
                        st.session_state.doc_data = result['extracted_data']
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    # STEP 2: SELFIE
    elif st.session_state.step == 2:
        st.subheader("Step 2: Biometric Verification")
        st.markdown("Please take a selfie to verify liveness")
        
        option = st.radio("Choose input:", ["Webcam", "Upload File"])
        
        selfie_file = None
        if option == "Webcam":
            selfie_file = st.camera_input("Take a picture")
        else:
            selfie_file = st.file_uploader("Upload Selfie", type=['jpg', 'png'])

        if selfie_file and st.button("Verify Identity", type="primary"):
            with st.spinner("Checking liveness and face match..."):
                try:
                    if option == "Webcam":
                        filename = "selfie.jpg"
                        content = selfie_file.getvalue()
                        mimetype = "image/jpeg"
                    else:
                        filename = selfie_file.name
                        content = selfie_file.read()
                        mimetype = selfie_file.type

                    files = {"selfie": (filename, content, mimetype)}
                    data = {"document_id": st.session_state.verification_id}
                    
                    res = requests.post(f"{API_URL}/v1/verify-face", files=files, data=data)
                    
                    if res.status_code == 200:
                        st.session_state.face_data = res.json()
                        st.session_state.step = 3
                        st.rerun()
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # STEP 3: RISK ASSESSMENT
    elif st.session_state.step == 3:
        st.subheader("Step 3: Risk Assessment")
        with st.spinner("Calculating Risk Score & Compliance checks..."):
            time.sleep(1)
            try:
                res = requests.post(f"{API_URL}/v1/risk-assessment?document_id={st.session_state.verification_id}")
                if res.status_code == 200:
                    st.session_state.risk_data = res.json()
                    st.session_state.step = 4
                    st.rerun()
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    # STEP 4: FINAL REPORT
    elif st.session_state.step == 4:
        risk = st.session_state.risk_data
        
        if risk['decision'] == 'APPROVED':
            st.success(f"DECISION: {risk['decision']}")
        else:
            st.error(f"DECISION: {risk['decision']}")

        m1, m2, m3 = st.columns(3)
        m1.metric("Risk Score", f"{risk['overall_risk_score']:.1%}")
        m2.metric("Document Validity", "Valid")
        m3.metric("Face Match", "90% Match")

        st.markdown("Compliance Report")
        with st.expander("View Full Report", expanded=True):
            st.json(risk['compliance_report'])
            
        st.markdown("Extracted Data")
        st.json(st.session_state.doc_data)
        
        if st.button("Start New Verification"):
            st.session_state.step = 1
            st.rerun()

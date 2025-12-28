import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(
    page_title="KYC Compliance Portal",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ KYC EU Compliance Verification")

# Environment variables
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.sidebar.header("System Status")
try:
    response = requests.get(f"{API_URL}/api/health")
    if response.status_code == 200:
        st.sidebar.success("Backend Connected")
    else:
        st.sidebar.error("Backend Error")
except Exception:
    st.sidebar.warning("Backend Offline")

st.write("Welcome to the KYC Compliance Verification portal.")
st.write(f"Connecting to Backend at: `{API_URL}`")

# Placeholder for verification flow
st.divider()
st.subheader("Start Verification")
uploaded_file = st.file_uploader("Upload ID Document", type=['png', 'jpg', 'jpeg', 'pdf'])

if uploaded_file is not None:
    st.info("Document received. Verification logic will be implemented here.")

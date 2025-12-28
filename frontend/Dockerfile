FROM python:3.10-slim

# Metadata
LABEL maintainer="Santiago Torterolo"
LABEL description="KYC Verification Frontend - Streamlit"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (only Streamlit subset)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit pandas requests Pillow numpy python-dateutil

# Copy application code
COPY frontend/app.py .
COPY frontend/.streamlit ./.streamlit/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
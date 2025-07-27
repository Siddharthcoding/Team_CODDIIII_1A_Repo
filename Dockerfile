# Use official Python image with AMD64 platform
FROM --platform=linux/amd64 python:3.9-slim

# Install system dependencies for PDF processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Create input/output directories
RUN mkdir -p /app/input && mkdir -p /app/output

# Entrypoint command
CMD ["python", "process_pdf.py"]
# ====================================================================
# Multi-stage Dockerfile: React Frontend Builder + FastAPI Runner
# ====================================================================

# --- STAGE 1: Build the Vite Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /build

# Install dependencies and build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Python FastAPI Backend Runner ---
# Default to python:3.10-slim.
# NOTE: If you are running GPU inference inside Docker on Coolify:
# You can replace this base image with a CUDA-ready image like:
# FROM nvcr.io/nvidia/pytorch:23.10-py3
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (e.g. git for clone, libgl for OpenCV/PIL if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI backend code
COPY backend/app ./backend/app

# Copy compiled frontend from Stage 1 into the path FastAPI expects
COPY --from=frontend-builder /build/dist ./frontend/dist

# Expose port and configure environment
EXPOSE 8000
ENV PORT=8000
ENV HOST=0.0.0.0
ENV MOCK_MODE=true

# Command to run uvicorn server
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

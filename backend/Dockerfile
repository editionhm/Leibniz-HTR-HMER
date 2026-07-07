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
# Use a pre-built PyTorch CUDA image. This avoids downloading 3GB of PyTorch from PyPI
# and ensures GPU support works out of the box on the RTX 3090.
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Install git (needed for Hugging Face and potential git installs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*


# Install python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install bitsandbytes (for 4-bit quantization) and xformers (for attention acceleration)
# compatible with PyTorch 2.2.0 & CUDA 12.1
RUN pip install --no-cache-dir bitsandbytes
RUN pip install --no-cache-dir --no-deps xformers==0.0.24
RUN pip install --no-cache-dir --no-deps trl peft upstream-unsloth
RUN pip install --no-cache-dir "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

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

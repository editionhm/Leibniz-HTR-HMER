# ====================================================================
# FastAPI entrypoint and routes serving logic
# ====================================================================
import os
import io
import traceback
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from PIL import Image


from .schemas import InferenceResponse, HealthResponse
from .prompts import get_prompt
from .inference import load_model, get_model_status, run_inference

# Lifecycle manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model weights on startup
    load_model()
    yield
    # Clean up resources if needed
    pass

app = FastAPI(
    title="Leibniz Manuscript Recognition API",
    description="Backend API for Leibniz HTR and HMER Demonstration Prototype",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints

@app.get("/api/health", response_model=HealthResponse)
async def health():
    """
    Checks backend status, GPU availability, and model config.
    """
    try:
        status_info = get_model_status()
        return HealthResponse(
            status=status_info["status"],
            gpu_available=status_info["gpu_available"],
            gpu_name=status_info["gpu_name"],
            model_loaded=status_info["model_loaded"],
            mock_mode=status_info["mock_mode"],
            config=status_info["config"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@app.post("/api/infer", response_model=InferenceResponse)
async def infer(
    image: UploadFile = File(...),
    task: str = Form(...),
    mode: Optional[str] = Form(None),
    candidate: Optional[str] = Form(None),
    tagged_candidate: Optional[str] = Form(None)
):
    """
    Exposes HTR and HMER inference.
    Receives image and task parameters.
    """
    # 1. Validation
    task_upper = task.upper()
    if task_upper not in ["HTR", "HMER"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task must be 'HTR' or 'HMER'"
        )
        
    if task_upper == "HMER":
        if not mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mode is required for task 'HMER'"
            )
        mode_lower = mode.lower()
        if mode_lower not in ["plain", "symbol_counting", "tree_cot", "detect_error", "correct_error"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid HMER mode. Choose from plain, symbol_counting, tree_cot, detect_error, correct_error."
            )
        if mode_lower == "detect_error" and not candidate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate formula (candidate) is required for Detect ERROR mode."
            )
        if mode_lower == "correct_error" and not tagged_candidate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tagged candidate formula (tagged_candidate) is required for Correct ERROR mode."
            )

    # 2. Read and parse image file
    try:
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}"
        )

    # 3. Retrieve and interpolate prompt
    try:
        prompt = get_prompt(
            task=task,
            mode=mode,
            candidate=candidate,
            tagged_candidate=tagged_candidate
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 4. Trigger inference
    try:
        result_text, latency = run_inference(
            image=pil_image,
            prompt=prompt,
            task=task,
            mode=mode,
            candidate=candidate,
            tagged_candidate=tagged_candidate
        )
        
        return InferenceResponse(
            task=task,
            mode=mode,
            prompt=prompt,
            result=result_text,
            latency_seconds=round(latency, 2)
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference process failed: {str(e)}"
        )

# Static files mounting logic for single container production distribution
FRONTEND_DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(FRONTEND_DIST_DIR):
    print(f"[Info] [Backend] Serving compiled frontend from: {FRONTEND_DIST_DIR}")
    # Mount frontend static directory
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST_DIR, "assets")), name="assets")
    
    # Catch-all route to serve the built index.html for UI SPA routes
    @app.get("/{catchall:path}", response_class=HTMLResponse)
    async def serve_frontend(catchall: str):
        # Allow API routes to slide through
        if catchall.startswith("api/") or catchall.startswith("docs") or catchall.startswith("openapi.json"):
            raise HTTPException(status_code=404)
        
        index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
else:
    print(f"[Warning] [Backend] Frontend dist directory not found at: {FRONTEND_DIST_DIR}")
    print("[Info] [Backend] Frontend must be run separately using Vite dev server (npm run dev).")

    
    @app.get("/")
    async def index_root():
        return {
            "name": "Leibniz Manuscript Recognition Demo API",
            "info": "To view the webapp interface, run the frontend Vite dev server or build the frontend project."
        }

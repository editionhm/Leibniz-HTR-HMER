# Leibniz Manuscript Recognition Demo (HTR & HMER)

An elegant, modern, and academic web application prototype demonstrating handwritten text recognition (HTR) and handwritten mathematical expression recognition (HMER) for Gottfried Wilhelm Leibniz's historical manuscripts.

This system demonstrates that a unified interface can support both tasks using a fine-tuned Qwen vision-language model, testing multiple prompting strategies for mathematics.

---

## Features

1. **HTR (Handwritten Text Recognition)**: Simple transcription of handwritten German/Latin texts.
2. **HMER (Handwritten Mathematical Expression Recognition)**: Five advanced prompt strategies:
   - **Plain**: Direct translation of images into raw LaTeX.
   - **Symbol Counting**: Dynamic identification and counting of distinct mathematical symbols prior to LaTeX output.
   - **Tree CoT**: Generation of an Abstract Syntax Tree (AST) showing semantic math hierarchies, followed by LaTeX output.
   - **Detect ERROR (EDL Detection)**: Comparative OCR analysis to identify and flag errors using `<error_start>`, `<error_end>`, and `<deleted>` tags.
   - **Correct ERROR (EDL Correction)**: Operational logging (REPLACE, INSERT, DELETE) to resolve flagged errors and produce correct LaTeX.
3. **KaTeX live rendering**: Direct visual rendering of HMER LaTeX formulas.
4. **Data pipeline buttons**: Seamless chaining buttons ("Use as candidate", "Use as tagged candidate") that feed results into subsequent error-checking tasks.
5. **Session History**: Fast comparison of previous runs and parameters in the active session.
6. **Dockerized Setup**: Single-container deployment served directly via FastAPI (no CORS issues in production).
7. **Mock mode fallback**: Full functional testing on local hardware without CUDA GPU support.

---

## Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI server & static files distribution
│   │   ├── inference.py     # Unsloth weights loader and inference logic
│   │   ├── prompts.py       # Prompt templates for HTR/HMER
│   │   └── schemas.py       # API schema definitions
│   ├── requirements.txt     # Python requirements
│   └── Dockerfile           # Multi-stage production container build
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (UploadZone, ControlPanel, ResultPanel, HistoryPanel)
│   │   ├── App.jsx          # React app manager
│   │   └── index.css        # Archives-themed styling
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml       # Configuration for Docker Compose
├── .env.example             # Template for variables
└── README.md                # This instructions manual
```

---

## 🛠️ Local Installation & Development

### 1. Backend Setup
1. Open a terminal in the `backend/` directory.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
5. Run the FastAPI development server:
   ```bash
   python -m uvicorn backend.app.main:app --reload --port 8000
   ```

### 2. Frontend Setup
1. Open a terminal in the `frontend/` directory.
2. Install node packages:
   ```bash
   npm install
   ```
3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser at `http://localhost:5173`. Any API calls to `/api/*` will automatically be proxied to `http://localhost:8000`.

---

## 💡 Connecting Your Fine-tuned Model (Unsloth)

To run the model on your RTX 3090, you must configure the environment variables:

1. **Extract your checkpoint**: Unzip the checkpoint file (e.g., `best_clean_htr_plain_exprate.zip` containing the LoRA adapter configurations `adapter_config.json`, `adapter_model.safetensors`, etc.) to a local directory, for example:
   `j:/UnivHm_NextJS/checkpoints/best_clean_htr_plain_exprate`
2. **Configure your `.env`**:
   Disable mock mode, set the correct device, and define the base model path and LoRA adapter path:
   ```ini
   MOCK_MODE=false
   DEVICE=cuda
   LOAD_IN_4BIT=true
   MODEL_NAME_OR_PATH=Qwen/Qwen2-VL-2B-Instruct
   LORA_ADAPTER_PATH=j:/UnivHm_NextJS/checkpoints/best_clean_htr_plain_exprate
   ```
3. **Unsloth Installation Note**:
   Unsloth requires specialized installation depending on your PyTorch and CUDA versions. When running GPU inference, ensure Unsloth is installed in your python environment:
   ```bash
   pip install --no-deps "xformers<0.0.26" trl peft upstream-unsloth
   pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
   ```

---

## 🚀 Coolify & VPS Deployment

The application is dockerized to build the frontend assets, copy them to the FastAPI directory, and serve everything as a single container. This simplifies Coolify SSL reverse proxies.

### Coolify Setup:
1. In the Coolify dashboard, select **Create New Resource** -> **Git Repository**.
2. Connect your GitHub repository.
3. Choose **Docker Compose** or **Dockerfile** as the build pack.
   - *If using Docker Compose*: Point to the root `docker-compose.yml`. Coolify will automatically configure port `8000`.
   - *If using Dockerfile*: Point the Dockerfile path to `backend/Dockerfile` and set the build context to the root `.`.
4. Add the following environment variables in the Coolify configuration UI:
   - `MOCK_MODE=false` (or `true` if testing container health check without GPU)
   - `MODEL_NAME_OR_PATH=Qwen/Qwen2-VL-2B-Instruct`
   - `LORA_ADAPTER_PATH=/app/checkpoints/best_clean` (Mount your volume containing the model weights inside `/app/checkpoints` in the container)
5. Under GPU configuration, check **Enable GPU access** (requires `nvidia-container-toolkit` installed on your VPS host). Coolify will automatically inject the GPU variables into the container environment.
6. Click **Deploy**.

---

## 🛰️ API Endpoints

### 1. `POST /api/infer`
Initiates recognition logic.
- **Payload (Multipart Form-Data)**:
  - `image`: Image file binary
  - `task`: `"HTR"` or `"HMER"`
  - `mode`: (Only for HMER) `"plain"`, `"symbol_counting"`, `"tree_cot"`, `"detect_error"`, or `"correct_error"`
  - `candidate`: (Only for HMER `detect_error`) string formula
  - `tagged_candidate`: (Only for HMER `correct_error`) tagged formula

- **Response (JSON)**:
  ```json
  {
    "task": "HMER",
    "mode": "plain",
    "prompt": "I have an image of a handwritten mathematical expression...",
    "result": "\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}",
    "latency_seconds": 1.45
  }
  ```

### 2. `GET /api/health`
Monitors hardware capabilities.
- **Response (JSON)**:
  ```json
  {
    "status": "online",
    "gpu_available": true,
    "gpu_name": "NVIDIA GeForce RTX 3090",
    "model_loaded": true,
    "mock_mode": false,
    "config": {
      "model_name_or_path": "Qwen/Qwen2-VL-2B-Instruct",
      "lora_adapter_path": "/app/checkpoints/best_clean",
      "load_in_4bit": true,
      "device": "cuda",
      "max_new_tokens": 512,
      "temperature": 0.0
    }
  }
  ```

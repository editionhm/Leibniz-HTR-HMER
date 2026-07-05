# ====================================================================
# Model loading and inference logic (Unsloth + Mock Mode)
# ====================================================================
import os
import time
import random
from PIL import Image

# Read configuration from environment
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
MODEL_NAME_OR_PATH = os.getenv("MODEL_NAME_OR_PATH", "Qwen/Qwen2-VL-2B-Instruct")
LORA_ADAPTER_PATH = os.getenv("LORA_ADAPTER_PATH", "")
DEVICE = os.getenv("DEVICE", "cuda")
LOAD_IN_4BIT = os.getenv("LOAD_IN_4BIT", "true").lower() == "true"
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

# Global model and tokenizer
model = None
tokenizer = None
model_loaded = False
backend_warning = ""

def load_model():
    """
    Initializes and loads the model into memory.
    If MOCK_MODE is True, runs in simulated mode.
    """
    global model, tokenizer, model_loaded, backend_warning
    
    if MOCK_MODE:
        print("[Info] [Backend] Running in MOCK MODE. No model weights will be loaded.")
        model_loaded = True
        return
        
    print(f"[Info] [Backend] Loading base model: {MODEL_NAME_OR_PATH} (4-bit={LOAD_IN_4BIT})...")
    try:
        import torch
        from unsloth import FastVisionModel
        
        # Load the base vision-language model using Unsloth
        model, tokenizer = FastVisionModel.from_pretrained(
            model_name=MODEL_NAME_OR_PATH,
            load_in_4bit=LOAD_IN_4BIT,
            device_map="auto" if DEVICE == "cuda" else "cpu"
        )
        
        # Load LoRA adapter if provided
        if LORA_ADAPTER_PATH and os.path.exists(LORA_ADAPTER_PATH):
            print(f"[Info] [Backend] Loading LoRA adapter: {LORA_ADAPTER_PATH}...")
            model.load_adapter(LORA_ADAPTER_PATH)
        elif LORA_ADAPTER_PATH:
            print(f"[Warning] [Backend] LoRA adapter path '{LORA_ADAPTER_PATH}' was specified but does not exist!")
            backend_warning = f"LoRA adapter path '{LORA_ADAPTER_PATH}' not found. Loaded base model only."
            
        # Enable 2x faster native inference
        if hasattr(FastVisionModel, "for_inference"):
            FastVisionModel.for_inference(model)
            
        model_loaded = True
        print("[Success] [Backend] Model successfully loaded on GPU!")
        
    except ImportError as e:
        print(f"[Warning] [Backend] Error importing Unsloth or PyTorch: {str(e)}")
        print("[Info] [Backend] Falling back to MOCK MODE.")
        backend_warning = "Unsloth/PyTorch not installed or compatible. Switched to MOCK_MODE."
        model_loaded = True # We set this to true so the app remains responsive in mock fallback
    except Exception as e:
        print(f"[Error] [Backend] Failed to load model: {str(e)}")
        print("[Info] [Backend] Falling back to MOCK MODE.")
        backend_warning = f"Failed to load weights: {str(e)}. Switched to MOCK_MODE."
        model_loaded = True


def get_model_status():
    """
    Returns information about CUDA capability, model paths, and mock state.
    """
    gpu_available = False
    gpu_name = None
    
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            gpu_name = torch.cuda.get_device_name(0)
    except ImportError:
        pass
        
    return {
        "status": "online" if model_loaded else "loading",
        "gpu_available": gpu_available,
        "gpu_name": gpu_name,
        "model_loaded": model_loaded,
        "mock_mode": MOCK_MODE or (backend_warning != ""),
        "config": {
            "model_name_or_path": MODEL_NAME_OR_PATH,
            "lora_adapter_path": LORA_ADAPTER_PATH,
            "load_in_4bit": LOAD_IN_4BIT,
            "device": DEVICE,
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "warning": backend_warning
        }
    }

def run_inference(image: Image.Image, prompt: str, task: str, mode: str = None, candidate: str = None, tagged_candidate: str = None) -> tuple[str, float]:
    """
    Executes inference. Under MOCK_MODE, simulates realistic output.
    Returns: (result_text, latency_seconds)
    """
    start_time = time.time()
    
    is_mock = MOCK_MODE or (model is None or tokenizer is None)
    
    if is_mock:
        # Simulate network/inference latency (1.0s to 2.5s)
        time.sleep(random.uniform(1.0, 2.5))
        
        result = _generate_mock_result(task, mode, candidate, tagged_candidate)
        latency = time.time() - start_time
        return result, latency

    # Actual Unsloth GPU inference
    try:
        # standard Qwen2-VL Chat format
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        inputs = tokenizer(
            image,
            input_text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to("cuda")
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            use_cache=True
        )
        
        # Decode response, remove chat formatting
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up output (sometimes models output system headers, remove them if needed)
        if "content" in response:
            # Simple clean up if chat template structure leaks
            pass
            
        latency = time.time() - start_time
        return response.strip(), latency
        
    except Exception as e:
        print(f"❌ [Backend] Inference Error: {str(e)}")
        # Return error message to frontend
        return f"Inference Error: {str(e)}", time.time() - start_time

def _generate_mock_result(task: str, mode: str = None, candidate: str = None, tagged_candidate: str = None) -> str:
    """
    Generates realistic looking results matching Leibniz style and LaTeX math.
    """
    # HTR Mock outputs
    htr_samples = [
        "Nova methodus pro maximis et minimis, itemque tangentibus, quae nec fractas nec irrationales quantitates moratur, & singulare pro illis calculi genus.",
        "Ex datis aequationibus differentialibus invenire aequationes integrales. Ut in integratione dy = x dx fit y = 1/2 x^2 + C, quod est initium calculi integralis.",
        "Nihil est sine ratione. Cùm Deus calculat et cogitationem exercet, fit mundus. Hanc ideam in specimine meo algebraico explicavi.",
        "Dum Deus calculat et cogitationem exercet, fit mundus, et res perfectissime ordinantur. Signum integralis primum a me anno 1675 adhibitum est.",
        "Ut calculus differentialis sit utilis ad inveniendas tangentes curves, oportet dy/dx definire tanquam limitem rationis differentiarum."
    ]
    
    # HMER Mock outputs (Plain formulas)
    math_formulas = [
        r"\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}",
        r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}",
        r"d(xy) = x\,dy + y\,dx",
        r"\int x^n dx = \frac{x^{n+1}}{n+1}",
        r"e^{i\pi} + 1 = 0",
        r"\oint_C \mathbf{F} \cdot d\mathbf{r} = \iint_S (\nabla \times \mathbf{F}) \cdot d\mathbf{A}"
    ]

    if task.upper() == "HTR":
        return random.choice(htr_samples)
        
    # HMER Tasks
    mode_lower = mode.lower() if mode else "plain"
    
    if mode_lower == "plain":
        return random.choice(math_formulas)
        
    elif mode_lower == "symbol_counting":
        formula = random.choice(math_formulas)
        # Parse basic symbols in a mock structured format
        if r"\int" in formula:
            return (
                "Detected symbols:\n"
                "- Integral symbol (\\int): 1\n"
                "- Lower limit (0): 1\n"
                "- Upper limit (\\infty): 1\n"
                "- Euler constant (e): 1\n"
                "- Variable (x): 2\n"
                "- Subscript/Superscript: 2\n"
                "- Fraction (\\frac): 1\n"
                "- Square root (\\sqrt): 1\n"
                "- Pi symbol (\\pi): 1\n"
                "- Equals sign (=): 1\n\n"
                f"Formula LaTeX: {formula}"
            )
        elif r"\sum" in formula:
            return (
                "Detected symbols:\n"
                "- Summation symbol (\\sum): 1\n"
                "- Variable (n): 2\n"
                "- Infinity (\\infty): 1\n"
                "- Fraction (\\frac): 1\n"
                "- Equal sign (=): 1\n"
                "- Pi symbol (\\pi): 1\n\n"
                f"Formula LaTeX: {formula}"
            )
        else:
            return (
                "Detected symbols:\n"
                "- Variable (x): 2\n"
                "- Variable (y): 2\n"
                "- Differential (d): 3\n"
                "- Equal sign (=): 1\n"
                "- Plus sign (+): 1\n\n"
                f"Formula LaTeX: {formula}"
            )
            
    elif mode_lower == "tree_cot":
        formula = random.choice(math_formulas)
        if r"\int" in formula:
            return (
                "Abstract Syntax Tree (AST):\n"
                "└── EQUALS\n"
                "    ├── INTEGRAL [limits: 0 -> \\infty]\n"
                "    │   └── MULTIPLY\n"
                "    │       ├── POWER\n"
                "    │       │   ├── e\n"
                "    │       │   └── NEGATIVE\n"
                "    │       │       └── POWER [x, 2]\n"
                "    │       └── dx\n"
                "    └── DIVISION\n"
                "        ├── SQRT\n"
                "        │   └── \\pi\n"
                "        └── 2\n\n"
                f"Formula LaTeX: {formula}"
            )
        else:
            return (
                "Abstract Syntax Tree (AST):\n"
                "└── EQUALS\n"
                "    ├── DIFFERENTIAL\n"
                "    │   └── MULTIPLY [x, y]\n"
                "    └── ADD\n"
                "        ├── MULTIPLY [x, dy]\n"
                "        └── MULTIPLY [y, dx]\n\n"
                f"Formula LaTeX: {formula}"
            )
            
    elif mode_lower == "detect_error":
        cand = candidate if candidate else r"\int_0^\infty e^{-x} dx = \frac{\pi}{2}"
        # We simulate finding an error in the candidate formula and wrap it in tags
        # E.g. replace "e^{-x}" with "e^{-x <error_start> <error_end> <deleted> ^2}" 
        # or similar depending on candidate contents
        if "e^{-x}" in cand:
            marked = cand.replace("e^{-x}", r"e^{-x <error_start> <error_end> <deleted> ^2}")
        elif r"\frac{\pi}{2}" in cand:
            marked = cand.replace(r"\frac{\pi}{2}", r"\frac{<error_start> \pi <error_end> \sqrt{\pi}}{2}")
        elif "dx" in cand:
            marked = cand.replace("dx", "d <error_start> x <error_end> t")
        else:
            marked = f"{cand} <error_start> <error_end> <deleted> + C"
            
        return marked
        
    elif mode_lower == "correct_error":
        tagged = tagged_candidate if tagged_candidate else r"\int_0^\infty e^{-x <error_start> <error_end> <deleted> ^2} dx = \frac{\pi}{2}"
        
        # Parse basic tags and show correction log
        log = "Correction Operations:\n"
        corrected = tagged
        
        if "<deleted> ^2" in tagged or "<deleted>^2" in tagged:
            log += "- INSERT: \"^2\" at position 15 (after -x)\n"
            corrected = tagged.replace("<error_start> <error_end> <deleted> ^2", "^2").replace("<error_start> <error_end> <deleted>^2", "^2")
        elif "error_start" in tagged:
            # Fallback simple replacement of tags
            log += "- REPLACE: erroneous segment with corrected LaTeX expression\n"
            # Remove tags and just keep the second part inside the error zone or do basic cleaning
            # For demonstration, we'll strip tags and clean the math formula
            import re
            corrected = re.sub(r"<error_start>.*<error_end>\s*", "", tagged)
            corrected = corrected.replace("<deleted>", "")
            
        log += f"\nCorrected LaTeX: {corrected}"
        return log

    return "No result generated."

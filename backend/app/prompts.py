# ====================================================================
# Prompts for HTR and HMER tasks
# ====================================================================

# HTR Prompt
HTR_PROMPT = "I have an image of a handwritten text. Please transcribe the handwritten text as accurately as possible."

# HMER Prompts
HMER_PLAIN = "I have an image of a handwritten mathematical expression. Please write out the expression of the formula in the image using LaTeX format"

HMER_SYMBOL_COUNTING = "I have an image of a handwritten mathematical expression. Please identify and count each distinct visible mathematical symbol in the image, and then provide its corresponding LaTeX format"

HMER_TREE_COT = "I have an image of a handwritten mathematical expression. Please generate the abstract syntax tree (AST) of the formula in the image, and then provide its corresponding LaTeX format."

HMER_DETECT_ERROR_TEMPLATE = (
    "I have an image of a handwritten mathematical expression and its OCR recognition result. "
    "Please help me to detect possible errors in the recognition result and mark the places where "
    "errors occur with <error_start> <error_end> and <deleted>.\n"
    "erroneous formula: {candidate}\n"
    "Marked formula:"
)

HMER_CORRECT_ERROR_TEMPLATE = (
    "I have an image of a handwritten mathematical expression and a predicted formula with error tags, "
    "correct the formula by modifying the parts marked with <error_start> and <error_end> and "
    "inserting content where <deleted> are present. Output the modifications as REPLACE, INSERT, or DELETE operations.\n"
    "Marked formula: {tagged_candidate}\n"
    "Correction log:"
)

def get_prompt(task: str, mode: str = None, candidate: str = None, tagged_candidate: str = None) -> str:
    """
    Returns the appropriate prompt for the given task and mode.
    Handles dynamic interpolation for Error Detection and Correction.
    """
    if task.upper() == "HTR":
        return HTR_PROMPT
    
    if task.upper() == "HMER":
        if not mode:
            raise ValueError("HMER mode must be specified (plain, symbol_counting, tree_cot, detect_error, correct_error)")
        
        mode_lower = mode.lower()
        if mode_lower == "plain":
            return HMER_PLAIN
        elif mode_lower == "symbol_counting":
            return HMER_SYMBOL_COUNTING
        elif mode_lower == "tree_cot":
            return HMER_TREE_COT
        elif mode_lower == "detect_error":
            if not candidate:
                raise ValueError("Candidate formula is required for Detect ERROR mode.")
            return HMER_DETECT_ERROR_TEMPLATE.format(candidate=candidate)
        elif mode_lower == "correct_error":
            if not tagged_candidate:
                raise ValueError("Tagged candidate formula is required for Correct ERROR mode.")
            return HMER_CORRECT_ERROR_TEMPLATE.format(tagged_candidate=tagged_candidate)
        else:
            raise ValueError(f"Unknown HMER mode: {mode}")
            
    raise ValueError(f"Unknown task: {task}")

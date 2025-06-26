import json
from pathlib import Path
from ocr.ocr_engine import extract_text_from_file
from llm.llm_client import extract_fields_from_text
from config.doc_config import (
    get_document_config,
    get_prompt_path,
    get_validator_function,
    get_postprocess_function
)

def process_document(file_path: str, document_type: str) -> str:
    """
    Process a document: OCR, prompt, LLM extraction, validation, postprocessing.
    Args:
        file_path: Path to the input file
        document_type: Document type (e.g., 'resume', 'license', 'receipt')
    Returns:
        Validated and postprocessed data as JSON
    """
    # 1. OCR
    ocr_text = extract_text_from_file(file_path)
    if not ocr_text:
        raise ValueError(f"No text extracted from {file_path}")

    # 2. Load config for document type
    try:
        config = get_document_config(document_type)
    except Exception as e:
        raise ValueError(f"Unsupported document type: {document_type}. {e}")

    # 3. Load prompt
    prompt_path = get_prompt_path(document_type)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    # 4. LLM extraction
    data = extract_fields_from_text(ocr_text, prompt)

    # 5. Validate output
    validator_fn = get_validator_function(document_type)
    try:
        validated = validator_fn(data)
    except Exception as e:
        raise ValueError(f"Validation failed for {document_type}: {e}")

    # 6. Postprocess output
    postprocess_fn = get_postprocess_function(document_type)
    try:
        postprocessed = postprocess_fn(validated)
    except Exception as e:
        raise ValueError(f"Postprocessing failed for {document_type}: {e}")

    # 7. Return as JSON
    return json.dumps(postprocessed, ensure_ascii=False, indent=2) 
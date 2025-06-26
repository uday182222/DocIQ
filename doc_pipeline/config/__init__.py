"""
Configuration package for DOC-IQ document processing pipeline.
"""

from .doc_config import (
    get_document_config,
    get_supported_document_types,
    validate_document_type,
    get_prompt_path,
    get_validator_function,
    get_postprocess_function,
    DOCUMENT_CONFIGS
)

__all__ = [
    'get_document_config',
    'get_supported_document_types', 
    'validate_document_type',
    'get_prompt_path',
    'get_validator_function',
    'get_postprocess_function',
    'DOCUMENT_CONFIGS'
] 
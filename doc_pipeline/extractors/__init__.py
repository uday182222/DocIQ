"""
Extractors package for document-type-specific parsing.
"""

from .license import parse_license, get_expected_fields
from .receipt import *
# from .resume import *  # Will be added after creation

__all__ = ["parse_license", "get_expected_fields"] 
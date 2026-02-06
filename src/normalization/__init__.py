"""Normalization package for code normalization."""

from src.normalization.base import BaseNormalizer
from src.normalization.python_normalizer import PythonNormalizer
from src.normalization.cpp_normalizer import CppNormalizer
from src.normalization.java_normalizer import JavaNormalizer

# Factory function to get appropriate normalizer
def get_normalizer(language: str) -> BaseNormalizer:
    """
    Get normalizer for specified language.
    
    Args:
        language: Programming language ('python', 'cpp', 'java')
    
    Returns:
        Appropriate normalizer instance
    
    Raises:
        ValueError: If language not supported
    """
    normalizers = {
        'python': PythonNormalizer,
        'cpp': CppNormalizer,
        'java': JavaNormalizer
    }
    
    if language not in normalizers:
        raise ValueError(f"Unsupported language: {language}")
    
    return normalizers[language]()

__all__ = [
    'BaseNormalizer',
    'PythonNormalizer',
    'CppNormalizer',
    'JavaNormalizer',
    'get_normalizer'
]

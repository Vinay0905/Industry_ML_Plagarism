"""Normalization package for code normalization."""

from src.normalization.base import BaseNormalizer
from src.normalization.python_normalizer import PythonNormalizer
from src.normalization.cpp_normalizer import CppNormalizer
from src.normalization.java_normalizer import JavaNormalizer
from src.normalization.token_normalizer import TokenNormalizer

# Factory function to get appropriate normalizer
def get_normalizer(language: str, method: str = 'token') -> BaseNormalizer:
    """
    Get normalizer for specified language.
    
    Args:
        language: Programming language ('python', 'cpp', 'java')
        method: Normalization method:
            - 'token' (default): Fast universal token-based normalization
            - 'ast': Language-specific AST-based (Python only)
            - 'regex': Language-specific regex-based (C++, Java)
    
    Returns:
        Appropriate normalizer instance
    
    Raises:
        ValueError: If language or method not supported
    """
    # Universal token normalizer (recommended - works for all languages)
    if method == 'token':
        return TokenNormalizer()
    
    # Language-specific normalizers
    if method == 'ast' and language == 'python':
        return PythonNormalizer()
    elif method == 'regex':
        normalizers = {
            'python': PythonNormalizer,  # Falls back to AST
            'cpp': CppNormalizer,
            'java': JavaNormalizer
        }
        if language not in normalizers:
            raise ValueError(f"Unsupported language: {language}")
        return normalizers[language]()
    else:
        raise ValueError(f"Unsupported method '{method}' for language '{language}'")

__all__ = [
    'BaseNormalizer',
    'PythonNormalizer',
    'CppNormalizer',
    'JavaNormalizer',
    'TokenNormalizer',
    'get_normalizer'
]

__all__ = [
    'BaseNormalizer',
    'PythonNormalizer',
    'CppNormalizer',
    'JavaNormalizer',
    'get_normalizer'
]

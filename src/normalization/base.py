"""
Base normalizer interface for code normalization.
All language-specific normalizers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

class BaseNormalizer(ABC):
    """
    Abstract base class for code normalization.
    
    Normalization process:
    1. Remove comments and docstrings
    2. Normalize whitespace
    3. Normalize identifiers (var_1, func_1, etc.)
    4. Canonicalize control structures
    5. Preserve semantic meaning
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize normalizer with configuration.
        
        Args:
            config: Configuration dictionary (uses defaults if None)
        """
        from src.config.settings import NORMALIZATION_CONFIG
        
        self.config = config or NORMALIZATION_CONFIG
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Mapping of original identifiers to normalized ones
        self.identifier_map = {}
        self.var_counter = 0
        self.func_counter = 0
        self.class_counter = 0
    
    @abstractmethod
    def normalize(self, code: str) -> str:
        """
        Main normalization method.
        
        Args:
            code: Original source code
        
        Returns:
            Normalized code
        """
        pass
    
    @abstractmethod
    def remove_comments(self, code: str) -> str:
        """
        Remove all comments from code.
        
        Args:
            code: Source code with comments
        
        Returns:
            Code without comments
        """
        pass
    
    def normalize_whitespace(self, code: str) -> str:
        """
        Normalize whitespace (default implementation).
        
        Args:
            code: Source code
        
        Returns:
            Code with normalized whitespace
        """
        from src.utils.helpers import normalize_whitespace
        return normalize_whitespace(code)
    
    @abstractmethod
    def normalize_identifiers(self, code: str) -> str:
        """
        Normalize variable/function names to canonical form.
        
        Args:
            code: Source code
        
        Returns:
            Code with normalized identifiers
        """
        pass
    
    @abstractmethod
    def canonicalize_structures(self, code: str) -> str:
        """
        Canonicalize control flow structures.
        
        Args:
            code: Source code
        
        Returns:
            Code with canonicalized structures
        """
        pass
    
    def get_identifier_map(self) -> Dict[str, str]:
        """
        Get mapping of original to normalized identifiers.
        
        Returns:
            Dictionary mapping original names to normalized names
        """
        return self.identifier_map.copy()
    
    def reset_counters(self):
        """Reset identifier counters for new normalization."""
        self.identifier_map = {}
        self.var_counter = 0
        self.func_counter = 0
        self.class_counter = 0

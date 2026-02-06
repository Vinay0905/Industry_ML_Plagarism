"""
C++ code normalizer.
Simplified implementation using regex patterns.
For production, would use libclang or tree-sitter.
"""

import re
from typing import Dict, Any

from src.normalization.base import BaseNormalizer

class CppNormalizer(BaseNormalizer):
    """
    C++ code normalizer using regex patterns.
    Note: This is a simplified implementation for prototyping.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.cpp_keywords = self._get_cpp_keywords()
    
    def normalize(self, code: str) -> str:
        """
        Normalize C++ code.
        
        Args:
            code: Original C++ code
        
        Returns:
            Normalized C++ code
        """
        self.reset_counters()
        
        # Stage 1: Remove comments
        if self.config.get('remove_comments', True):
            code = self.remove_comments(code)
        
        # Stage 2: Normalize whitespace
        if self.config.get('normalize_whitespace', True):
            code = self.normalize_whitespace(code)
        
        # Stage 3: Normalize identifiers
        if self.config.get('normalize_identifiers', True):
            code = self.normalize_identifiers(code)
        
        # Stage 4: Canonicalize structures (future)
        if self.config.get('canonicalize_control_flow', True):
            code = self.canonicalize_structures(code)
        
        return code
    
    def remove_comments(self, code: str) -> str:
        """
        Remove C++ comments (// and /* */).
        
        Args:
            code: C++ code with comments
        
        Returns:
            Code without comments
        """
        # Remove multi-line comments /* */
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments //
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        
        return code
    
    def normalize_identifiers(self, code: str) -> str:
        """
        Normalize C++ identifiers.
        
        Args:
            code: C++ code
        
        Returns:
            Code with normalized identifiers
        """
        # Find all identifiers (simplified)
        identifier_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        def replace_identifier(match):
            name = match.group(1)
            
            # Preserve keywords and standard library
            if name in self.cpp_keywords or name.startswith('std'):
                return name
            
            # Check if function (followed by parenthesis)
            # This is a heuristic
            if name not in self.identifier_map:
                # Assume variable by default
                self.var_counter += 1
                self.identifier_map[name] = f"var_{self.var_counter}"
            
            return self.identifier_map[name]
        
        code = re.sub(identifier_pattern, replace_identifier, code)
        return code
    
    def canonicalize_structures(self, code: str) -> str:
        """
        Canonicalize C++ control structures.
        
        Args:
            code: C++ code
        
        Returns:
            Canonicalized code
        """
        # For now, return as-is
        # Future: normalize for/while, if-else patterns
        return code
    
    def _get_cpp_keywords(self) -> set:
        """Get set of C++ keywords to preserve."""
        return {
            'alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto',
            'bitand', 'bitor', 'bool', 'break', 'case', 'catch',
            'char', 'char8_t', 'char16_t', 'char32_t', 'class',
            'compl', 'concept', 'const', 'consteval', 'constexpr',
            'constinit', 'const_cast', 'continue', 'co_await',
            'co_return', 'co_yield', 'decltype', 'default', 'delete',
            'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit',
            'export', 'extern', 'false', 'float', 'for', 'friend',
            'goto', 'if', 'inline', 'int', 'long', 'mutable',
            'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr',
            'operator', 'or', 'or_eq', 'private', 'protected', 'public',
            'register', 'reinterpret_cast', 'requires', 'return',
            'short', 'signed', 'sizeof', 'static', 'static_assert',
            'static_cast', 'struct', 'switch', 'template', 'this',
            'thread_local', 'throw', 'true', 'try', 'typedef',
            'typeid', 'typename', 'union', 'unsigned', 'using',
            'virtual', 'void', 'volatile', 'wchar_t', 'while',
            'xor', 'xor_eq',
            # Common stdlib
            'cout', 'cin', 'endl', 'string', 'vector', 'map',
            'set', 'pair', 'queue', 'stack', 'iostream', 'algorithm'
        }

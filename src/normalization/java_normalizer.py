"""
Java code normalizer.
Simplified implementation using regex patterns.
For production, would use JavaParser or similar.
"""

import re
from typing import Dict, Any

from src.normalization.base import BaseNormalizer

class JavaNormalizer(BaseNormalizer):
    """
    Java code normalizer using regex patterns.
    Note: This is a simplified implementation for prototyping.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.java_keywords = self._get_java_keywords()
    
    def normalize(self, code: str) -> str:
        """
        Normalize Java code.
        
        Args:
            code: Original Java code
        
        Returns:
            Normalized Java code
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
        Remove Java comments (// and /* */ and /** */).
        
        Args:
            code: Java code with comments
        
        Returns:
            Code without comments
        """
        # Remove multi-line comments /* */ and Javadoc /** */
        code = re.sub(r'/\*\*?.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove single-line comments //
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        
        return code
    
    def normalize_identifiers(self, code: str) -> str:
        """
        Normalize Java identifiers.
        
        Args:
            code: Java code
        
        Returns:
            Code with normalized identifiers
        """
        # Find all identifiers
        identifier_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        def replace_identifier(match):
            name = match.group(1)
            
            # Preserve keywords and common Java classes
            if name in self.java_keywords or self._is_java_stdlib(name):
                return name
            
            if name not in self.identifier_map:
                # Heuristic: uppercase = class, lowercase = variable
                if name[0].isupper():
                    self.class_counter += 1
                    self.identifier_map[name] = f"Class_{self.class_counter}"
                else:
                    self.var_counter += 1
                    self.identifier_map[name] = f"var_{self.var_counter}"
            
            return self.identifier_map[name]
        
        code = re.sub(identifier_pattern, replace_identifier, code)
        return code
    
    def canonicalize_structures(self, code: str) -> str:
        """
        Canonicalize Java control structures.
        
        Args:
            code: Java code
        
        Returns:
            Canonicalized code
        """
        # For now, return as-is
        # Future: normalize for/while, if-else patterns
        return code
    
    def _get_java_keywords(self) -> set:
        """Get set of Java keywords to preserve."""
        return {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case',
            'catch', 'char', 'class', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extends', 'final',
            'finally', 'float', 'for', 'goto', 'if', 'implements',
            'import', 'instanceof', 'int', 'interface', 'long',
            'native', 'new', 'package', 'private', 'protected',
            'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw',
            'throws', 'transient', 'try', 'void', 'volatile', 'while',
            # Common modifiers
            'true', 'false', 'null'
        }
    
    def _is_java_stdlib(self, name: str) -> bool:
        """Check if name is likely from Java standard library."""
        stdlib_prefixes = ['System', 'String', 'Integer', 'Double',
                          'ArrayList', 'HashMap', 'List', 'Map', 'Set',
                          'Collection', 'Arrays', 'Math', 'Object']
        return name in stdlib_prefixes

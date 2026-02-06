"""
Universal token-based normalizer.
Works across Python, C++, and Java using regex tokenization.
This is a simplified, practical approach that's faster than AST parsing.
"""

import re
from typing import List, Dict
from src.normalization.base import BaseNormalizer

class TokenNormalizer(BaseNormalizer):
    """
    Universal token-based normalizer using regex.
    Works for Python, C++, Java, and similar languages.
    
    This is a lightweight alternative to AST-based normalization.
    """
    
    # Language keywords (common across Python/C++/Java)
    KEYWORDS = {
        "if", "else", "for", "while", "return",
        "break", "continue", "def", "import", "from",
        "class", "lambda", "elif", "in", "is",
        "not", "and", "or", "try", "except",
        "finally", "with", "as", "pass", "raise",
        "assert", "yield", "del", "global", "nonlocal",
        # C++/Java keywords
        "public", "private", "protected", "static",
        "void", "const", "virtual", "override",
        "new", "delete", "this", "super", "extends",
        "implements", "interface", "package", "throws",
        "catch", "switch", "case", "default", "do",
        "goto", "sizeof", "typedef", "struct", "union",
        "enum", "namespace", "using", "template"
    }
    
    # Common type keywords
    TYPES = {
        "int", "float", "double", "char", "bool",
        "void", "string", "str", "long", "short",
        "unsigned", "signed", "byte", "list", "dict",
        "set", "tuple", "array", "vector", "map"
    }
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
    
    def normalize(self, code: str) -> str:
        """
        Normalize code using token-based approach.
        
        Args:
            code: Source code to normalize
        
        Returns:
            Normalized code as space-separated tokens
        """
        if not isinstance(code, str):
            return ""
        
        # Reset counters for new normalization
        self.reset_counters()
        
        # Get normalized tokens
        tokens = self._normalize_to_tokens(code)
        
        # Join tokens with spaces for comparison
        return " ".join(tokens)
    
    def _normalize_to_tokens(self, code: str) -> List[str]:
        """
        Convert code to normalized token list.
        
        Args:
            code: Source code
        
        Returns:
            List of normalized tokens
        """
        # Decode literal \n, \t if they came via CSV
        try:
            code = code.encode("utf-8").decode("unicode_escape")
        except:
            pass  # If decoding fails, use as-is
        
        # Remove comments
        code = self.remove_comments(code)
        
        # Normalize whitespace
        code = re.sub(r"[ \t]+", " ", code)
        code = re.sub(r"\n\s*\n+", "\n", code)
        
        # Tokenize: identifiers, numbers, operators, punctuation
        tokens = re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*|\d+\.?\d*|==|!=|<=|>=|\+=|-=|\*=|/=|%=|&&|\|\||<<|>>|[%+\-*/<>=(){}\[\]:;,.]",
            code
        )
        
        # Normalize tokens
        norm_tokens = []
        for token in tokens:
            normalized = self._normalize_token(token)
            if normalized:  # Skip empty tokens
                norm_tokens.append(normalized)
        
        return norm_tokens
    
    def _normalize_token(self, token: str) -> str:
        """
        Normalize a single token.
        
        Args:
            token: Raw token
        
        Returns:
            Normalized token
        """
        token_lower = token.lower()
        
        # Keywords: keep as lowercase
        if token_lower in self.KEYWORDS:
            return token_lower
        
        # Type keywords: replace with TYPE
        if token_lower in self.TYPES:
            return "TYPE"
        
        # Numbers: replace with NUM
        if re.match(r"^\d+\.?\d*$", token):
            return "NUM"
        
        # Identifiers: map to VAR0, VAR1, etc.
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):
            if token not in self.identifier_map:
                self.var_counter += 1
                self.identifier_map[token] = f"VAR{self.var_counter}"
            return self.identifier_map[token]
        
        # Operators and punctuation: keep as-is
        return token
    
    def remove_comments(self, code: str) -> str:
        """
        Remove comments from code (Python, C++, Java).
        
        Args:
            code: Code with comments
        
        Returns:
            Code without comments
        """
        # Python comments (#)
        code = re.sub(r"#.*", "", code)
        
        # C++/Java single-line comments (//)
        code = re.sub(r"//.*", "", code)
        
        # C++/Java multi-line comments (/* */)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        
        return code
    
    def normalize_identifiers(self, code: str) -> str:
        """Not used in token-based approach - implemented via normalize()"""
        return code
    
    def canonicalize_structures(self, code: str) -> str:
        """Not used in token-based approach - handled by tokenization"""
        return code

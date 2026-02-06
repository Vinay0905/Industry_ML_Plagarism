"""
Python code normalizer using AST.
"""

import ast
import astor
import re
from typing import Dict, Any, Set

from src.normalization.base import BaseNormalizer

class PythonNormalizer(BaseNormalizer):
    """
    Python-specific code normalizer using AST transformations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.builtin_names = self._get_python_builtins()
    
    def normalize(self, code: str) -> str:
        """
        Normalize Python code through multi-stage process.
        
        Args:
            code: Original Python code
        
        Returns:
            Normalized Python code
        """
        self.reset_counters()
        
        try:
            # Stage 1: Remove comments
            if self.config.get('remove_comments', True):
                code = self.remove_comments(code)
            
            # Stage 2: Parse into AST
            tree = ast.parse(code)
            
            # Stage 3: Normalize identifiers
            if self.config.get('normalize_identifiers', True):
                tree = self._normalize_identifiers_ast(tree)
            
            # Stage 4: Canonicalize control structures
            if self.config.get('canonicalize_control_flow', True):
                tree = self._canonicalize_structures_ast(tree)
            
            # Stage 5: Convert back to code
            normalized_code = astor.to_source(tree)
            
            # Stage 6: Normalize whitespace
            if self.config.get('normalize_whitespace', True):
                normalized_code = self.normalize_whitespace(normalized_code)
            
            return normalized_code
            
        except SyntaxError as e:
            self.logger.error(f"Syntax error in Python code: {e}")
            # Return original code if parsing fails
            return code
    
    def remove_comments(self, code: str) -> str:
        """
        Remove comments and docstrings from Python code.
        
        Args:
            code: Python code with comments
        
        Returns:
            Code without comments
        """
        # Remove single-line comments
        lines = []
        for line in code.split('\n'):
            # Remove # comments but preserve strings
            if '#' in line:
                # Simple heuristic: if # is in quotes, keep it
                in_string = False
                quote_char = None
                cleaned = []
                for i, char in enumerate(line):
                    if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                            quote_char = None
                    if char == '#' and not in_string:
                        break
                    cleaned.append(char)
                line = ''.join(cleaned)
            lines.append(line)
        
        code = '\n'.join(lines)
        
        # Remove docstrings using AST
        try:
            tree = ast.parse(code)
            self._remove_docstrings_from_ast(tree)
            code = astor.to_source(tree)
        except:
            pass  # If parsing fails, return code as-is
        
        return code
    
    def _remove_docstrings_from_ast(self, node):
        """Remove docstrings from AST (in-place)."""
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            return
        
        # Remove docstring if present
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Str)):
            node.body.pop(0)
        
        # Recurse
        for child in ast.iter_child_nodes(node):
            self._remove_docstrings_from_ast(child)
    
    def normalize_identifiers(self, code: str) -> str:
        """Normalize using AST (called internally by normalize())."""
        return code  # Implemented via AST
    
    def _normalize_identifiers_ast(self, tree: ast.AST) -> ast.AST:
        """
        Normalize identifiers in AST.
        
        Renames variables to var_1, var_2, ...
        Renames functions to func_1, func_2, ...
        Renames classes to class_1, class_2, ...
        
        Preserves built-in names and standard library names.
        """
        transformer = IdentifierTransformer(self.builtin_names, self)
        tree = transformer.visit(tree)
        ast.fix_missing_locations(tree)
        return tree
    
    def canonicalize_structures(self, code: str) -> str:
        """Canonicalize using AST (called internally by normalize())."""
        return code  # Implemented via AST
    
    def _canonicalize_structures_ast(self, tree: ast.AST) -> ast.AST:
        """
        Canonicalize control flow structures.
        
        Currently keeps structures as-is.
        Future: Could normalize for/while equivalence, etc.
        """
        # For now, return as-is
        # In future, could implement:
        # - Convert range-based for to while
        # - Normalize if-elif-else to nested ifs
        # - etc.
        return tree
    
    def _get_python_builtins(self) -> Set[str]:
        """Get set of Python built-in names to preserve."""
        import builtins
        return set(dir(builtins))

class IdentifierTransformer(ast.NodeTransformer):
    """AST transformer to normalize identifiers."""
    
    def __init__(self, builtin_names: Set[str], normalizer: PythonNormalizer):
        self.builtin_names = builtin_names
        self.normalizer = normalizer
        self.name_map = {}
    
    def visit_Name(self, node):
        """Transform variable names."""
        if node.id in self.builtin_names:
            return node  # Preserve builtins
        
        if node.id not in self.name_map:
            self.normalizer.var_counter += 1
            self.name_map[node.id] = f"var_{self.normalizer.var_counter}"
            self.normalizer.identifier_map[node.id] = self.name_map[node.id]
        
        node.id = self.name_map[node.id]
        return node
    
    def visit_FunctionDef(self, node):
        """Transform function names."""
        if node.name not in self.builtin_names and node.name not in self.name_map:
            self.normalizer.func_counter += 1
            self.name_map[node.name] = f"func_{self.normalizer.func_counter}"
            self.normalizer.identifier_map[node.name] = self.name_map[node.name]
        
        if node.name in self.name_map:
            node.name = self.name_map[node.name]
        
        # Transform arguments
        for arg in node.args.args:
            if arg.arg not in self.builtin_names and arg.arg not in self.name_map:
                self.normalizer.var_counter += 1
                self.name_map[arg.arg] = f"var_{self.normalizer.var_counter}"
                self.normalizer.identifier_map[arg.arg] = self.name_map[arg.arg]
            if arg.arg in self.name_map:
                arg.arg = self.name_map[arg.arg]
        
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node):
        """Transform class names."""
        if node.name not in self.name_map:
            self.normalizer.class_counter += 1
            self.name_map[node.name] = f"class_{self.normalizer.class_counter}"
            self.normalizer.identifier_map[node.name] = self.name_map[node.name]
        
        node.name = self.name_map[node.name]
        self.generic_visit(node)
        return node

"""
Tree-sitter based structural similarity analyzer.
Multi-language AST parsing using tree-sitter (supports Python, Java, C++, C).

This is the RECOMMENDED structural similarity method for academic plagiarism detection.
"""

import logging
import textwrap
from typing import List, Dict, Set
from tree_sitter import Parser
from tree_sitter_languages import get_language

class TreeSitterStructuralAnalyzer:
    """
    Structural similarity using tree-sitter AST parsing.
    
    Advantages:
    - Multi-language support (Python, Java, C++, C)
    - Robust error handling (handles syntax errors gracefully)
    - Fast C-based parser
    - Industry-proven (used by GitHub, Atom, Neovim)
    """
    
    # Language mappings
    SUPPORTED_LANGUAGES = {
        'python': 'python',
        'java': 'java',
        'cpp': 'cpp',
        'c++': 'cpp',
        'c': 'c'
    }
    
    def __init__(self):
        """Initialize tree-sitter analyzer."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._language_cache = {}
        self._parser_cache = {}
    
    def _get_ts_language(self, language: str):
        """
        Get tree-sitter language object.
        
        Args:
            language: Language code ('python', 'java', 'cpp', 'c')
        
        Returns:
            Tree-sitter language object or None
        """
        lang = str(language).strip().lower()
        lang = self.SUPPORTED_LANGUAGES.get(lang)
        
        if not lang:
            self.logger.warning(f"Unsupported language: {language}")
            return None
        
        # Cache language objects
        if lang not in self._language_cache:
            try:
                self._language_cache[lang] = get_language(lang)
                self.logger.info(f"Successfully loaded tree-sitter language: {lang}")
            except Exception as e:
                self.logger.error(f"Failed to load language {lang}: {e}")
                return None
        
        return self._language_cache[lang]
    
    def _get_parser(self, language: str) -> Parser:
        """
        Get tree-sitter parser for language.
        
        Args:
            language: Language code
        
        Returns:
            Configured parser or None
        """
        ts_lang = self._get_ts_language(language)
        if not ts_lang:
            return None
        
        # Cache parsers
        if language not in self._parser_cache:
            # Support both old and new tree-sitter API
            # Old API (tree-sitter < 0.23.0): Parser() then set_language(...)
            # New API (tree-sitter >= 0.23.0): Parser(language=...)
            try:
                # Try old API first (for tree-sitter 0.20.4)
                parser = Parser()
                parser.set_language(ts_lang)
                self.logger.debug(f"Using old Parser API for {language}")
            except AttributeError:
                # Fall back to new API (tree-sitter >= 0.23.0)
                parser = Parser(language=ts_lang)
                self.logger.debug(f"Using new Parser API for {language}")
            
            self._parser_cache[language] = parser
        
        return self._parser_cache[language]

    
    def _clean_code(self, code: str) -> str:
        """
        Clean code for tree-sitter parsing.
        
        Args:
            code: Raw code string
        
        Returns:
            Cleaned code
        """
        if not isinstance(code, str):
            return ""
        
        # Decode literal escape sequences from CSV
        try:
            code = code.encode("utf-8").decode("unicode_escape")
        except:
            pass
        
        # Dedent and strip
        return textwrap.dedent(code.strip())
    
    def extract_ast_node_types(self, code: str, language: str = 'python') -> List[str]:
        """
        Extract AST node types from code using tree-sitter.
        
        Args:
            code: Source code
            language: Programming language
        
        Returns:
            List of AST node type strings
        """
        parser = self._get_parser(language)
        if not parser:
            self.logger.warning(f"No parser for language: {language}")
            return []
        
        # Clean code
        code = self._clean_code(code)
        if not code:
            return []
        
        try:
            # Parse code
            tree = parser.parse(bytes(code, "utf8"))
            root = tree.root_node
            
            # Skip if parse failed
            if root.type == "ERROR":
                self.logger.debug("Parse error - returning empty node list")
                return []
            
            # Extract node types via DFS
            node_types = []
            stack = [root]
            
            while stack:
                node = stack.pop()
                
                # Skip error nodes
                if node.type != "ERROR":
                    node_types.append(node.type)
                
                # Add children in reverse for DFS order
                stack.extend(reversed(node.children))
            
            return node_types
            
        except Exception as e:
            self.logger.error(f"Tree-sitter parsing failed: {e}")
            return []
    
    def compute_similarity(self, code1: str, code2: str, language: str = 'python') -> float:
        """
        Compute structural similarity between two code snippets.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language
        
        Returns:
            Similarity score (0-100)
        """
        # Extract AST node types
        nodes1 = self.extract_ast_node_types(code1, language)
        nodes2 = self.extract_ast_node_types(code2, language)
        
        # Handle empty ASTs
        if not nodes1 or not nodes2:
            self.logger.debug("One or both ASTs are empty")
            return 0.0
        
        # Compute Jaccard similarity
        set1 = set(nodes1)
        set2 = set(nodes2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        similarity = (intersection / union) * 100
        
        return similarity
    
    def get_detailed_similarity(
        self, 
        code1: str, 
        code2: str, 
        language: str = 'python'
    ) -> Dict:
        """
        Compute detailed structural similarity with breakdown.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language
        
        Returns:
            Dictionary with similarity score and details
        """
        nodes1 = self.extract_ast_node_types(code1, language)
        nodes2 = self.extract_ast_node_types(code2, language)
        
        if not nodes1 or not nodes2:
            return {
                'score': 0.0,
                'nodes1_count': len(nodes1),
                'nodes2_count': len(nodes2),
                'common_nodes': 0,
                'unique_to_1': 0,
                'unique_to_2': 0,
                'parse_success': False
            }
        
        set1 = set(nodes1)
        set2 = set(nodes2)
        
        intersection = set1 & set2
        union = set1 | set2
        
        similarity = (len(intersection) / len(union) * 100) if union else 0.0
        
        return {
            'score': similarity,
            'nodes1_count': len(nodes1),
            'nodes2_count': len(nodes2),
            'common_nodes': len(intersection),
            'unique_to_1': len(set1 - set2),
            'unique_to_2': len(set2 - set1),
            'parse_success': True,
            'common_node_types': sorted(intersection)[:10]  # Top 10 for brevity
        }

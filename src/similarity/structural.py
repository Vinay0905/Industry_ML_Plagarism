"""
Structural similarity analyzer with dual implementation:
1. AST-based (tree edit distance)
2. RK-GST (Rabin-Karp Greedy String Tiling)

This is a STRONG signal for plagiarism detection.
"""

import ast
import re
import logging
from typing import List, Dict, Tuple, Set
from enum import Enum
import numpy as np

from src.config.weights import (
    StructuralMethod, 
    HYBRID_WEIGHTS,
    AST_FEATURE_WEIGHTS,
    RKGST_CONFIG
)

# ============================================================================
# AST-BASED STRUCTURAL SIMILARITY
# ============================================================================

class ASTSimilarityAnalyzer:
    """
    AST-based structural similarity using tree edit distance.
    Good for: Deep algorithmic analysis, detecting refactored code
    """
    
    def __init__(self):
        self.feature_weights = AST_FEATURE_WEIGHTS
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def compute_similarity(self, code1: str, code2: str) -> float:
        """
        Compute AST-based similarity between two code snippets.
        Returns: 0-100% similarity score
        """
        try:
            # Parse both codes into ASTs
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)
            
            # Extract structural features
            features1 = self._extract_features(tree1)
            features2 = self._extract_features(tree2)
            
            # Compute similarity across multiple dimensions
            scores = {
                'tree_structure': self._tree_edit_distance(tree1, tree2),
                'control_flow': self._control_flow_similarity(features1, features2),
                'function_calls': self._function_call_similarity(features1, features2),
                'data_flow': self._data_flow_similarity(features1, features2)
            }
            
            # Weighted combination
            final_score = sum(
                scores[key] * self.feature_weights[key]
                for key in scores
            )
            
            return final_score * 100  # Convert to percentage
            
        except SyntaxError as e:
            # Fallback if code doesn't parse
            self.logger.warning(f"Syntax error in code: {e}")
            return 0.0
    
    def _extract_features(self, tree: ast.AST) -> dict:
        """Extract structural features from AST"""
        features = {
            'control_flow': [],
            'function_calls': [],
            'data_flow': [],
            'tree_fingerprint': []
        }
        
        for node in ast.walk(tree):
            # Control flow patterns
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                features['control_flow'].append(type(node).__name__)
            
            # Function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    features['function_calls'].append(node.func.id)
            
            # Tree structure fingerprint (node types)
            features['tree_fingerprint'].append(type(node).__name__)
        
        return features
    
    def _tree_edit_distance(self, tree1: ast.AST, tree2: ast.AST) -> float:
        """
        Compute normalized tree edit distance.
        Simplified version using sequence similarity on node types.
        """
        # Get tree fingerprints (sequence of node types)
        fp1 = [type(node).__name__ for node in ast.walk(tree1)]
        fp2 = [type(node).__name__ for node in ast.walk(tree2)]
        
        # Use sequence similarity (LCS-based)
        return self._sequence_similarity(fp1, fp2)
    
    def _control_flow_similarity(self, f1: dict, f2: dict) -> float:
        """Compare control flow patterns"""
        cf1 = f1['control_flow']
        cf2 = f2['control_flow']
        
        if not cf1 and not cf2:
            return 1.0
        if not cf1 or not cf2:
            return 0.0
        
        # Compare sequences of control structures
        return self._sequence_similarity(cf1, cf2)
    
    def _function_call_similarity(self, f1: dict, f2: dict) -> float:
        """Compare function call patterns"""
        calls1 = set(f1['function_calls'])
        calls2 = set(f2['function_calls'])
        
        if not calls1 and not calls2:
            return 1.0
        if not calls1 or not calls2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(calls1 & calls2)
        union = len(calls1 | calls2)
        return intersection / union if union > 0 else 0.0
    
    def _data_flow_similarity(self, f1: dict, f2: dict) -> float:
        """Compare data flow patterns (simplified)"""
        fp1 = f1['tree_fingerprint']
        fp2 = f2['tree_fingerprint']
        return self._sequence_similarity(fp1, fp2)
    
    def _sequence_similarity(self, seq1: list, seq2: list) -> float:
        """
        Compute similarity between two sequences using LCS.
        Returns: 0.0 to 1.0
        """
        if not seq1 or not seq2:
            return 0.0
        
        # Longest Common Subsequence
        lcs_length = self._lcs_length(seq1, seq2)
        max_length = max(len(seq1), len(seq2))
        
        return lcs_length / max_length if max_length > 0 else 0.0
    
    def _lcs_length(self, seq1: list, seq2: list) -> int:
        """Compute length of longest common subsequence"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]

# ============================================================================
# RK-GST STRUCTURAL SIMILARITY
# ============================================================================

class RKGSTSimilarityAnalyzer:
    """
    Rabin-Karp Greedy String Tiling similarity.
    Good for: Copy-paste detection, reordered code, fast screening
    """
    
    def __init__(self, min_match_length: int = None):
        """
        Args:
            min_match_length: Minimum token sequence length to consider a match
        """
        config = RKGST_CONFIG
        self.min_match_length = min_match_length or config['min_match_length']
        self.base = config['hash_base']
        self.prime = config['hash_prime']
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def compute_similarity(self, code1: str, code2: str) -> float:
        """
        Compute RK-GST similarity between two code snippets.
        Returns: 0-100% similarity score
        """
        # Tokenize both codes
        tokens1 = self._tokenize(code1)
        tokens2 = self._tokenize(code2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Find all maximal matches using greedy string tiling
        matches = self._greedy_string_tiling(tokens1, tokens2)
        
        # Compute coverage percentage
        coverage1 = self._compute_coverage(matches, len(tokens1), source=1)
        coverage2 = self._compute_coverage(matches, len(tokens2), source=2)
        
        # Average coverage (symmetric)
        similarity = (coverage1 + coverage2) / 2.0
        
        return similarity * 100  # Convert to percentage
    
    def _tokenize(self, code: str) -> list:
        """Tokenize code into semantic tokens."""
        # Pattern matches identifiers, numbers, and operators
        token_pattern = r'\b\w+\b|[+\-*/%=<>!&|^~(){}\[\];,.]'
        tokens = re.findall(token_pattern, code)
        
        # Filter out trivial tokens
        tokens = [t for t in tokens if t.strip()]
        
        return tokens
    
    def _greedy_string_tiling(self, tokens1: list, tokens2: list) -> list:
        """
        Greedy String Tiling algorithm to find maximal matches.
        Returns: List of matches: [(start1, start2, length), ...]
        """
        matches = []
        marked1 = [False] * len(tokens1)
        marked2 = [False] * len(tokens2)
        
        # Iteratively find longest unmarked matches
        while True:
            # Find longest match not yet marked
            best_match = self._find_longest_match(
                tokens1, tokens2, marked1, marked2
            )
            
            if best_match is None:
                break
            
            start1, start2, length = best_match
            
            if length < self.min_match_length:
                break
            
            # Mark this match
            for i in range(length):
                marked1[start1 + i] = True
                marked2[start2 + i] = True
            
            matches.append(best_match)
        
        return matches
    
    def _find_longest_match(
        self, 
        tokens1: list, 
        tokens2: list, 
        marked1: list, 
        marked2: list
    ) -> Tuple[int, int, int]:
        """Find longest unmarked matching substring."""
        max_length = 0
        best_match = None
        
        # Try all possible starting positions in tokens1
        for i in range(len(tokens1)):
            if marked1[i]:
                continue
            
            # Use Rabin-Karp to find matches in tokens2
            matches = self._rk_find_matches(
                tokens1, tokens2, i, marked1, marked2
            )
            
            for j, length in matches:
                if length > max_length:
                    max_length = length
                    best_match = (i, j, length)
        
        return best_match
    
    def _rk_find_matches(
        self,
        tokens1: list,
        tokens2: list,
        start1: int,
        marked1: list,
        marked2: list
    ) -> list:
        """Use Rabin-Karp rolling hash to find all matches."""
        matches = []
        
        # Maximum possible match length from this position
        max_len = len(tokens1) - start1
        
        # Try decreasing lengths (greedy: longest first)
        for length in range(max_len, self.min_match_length - 1, -1):
            # Check if any tokens in this range are marked
            if any(marked1[start1:start1 + length]):
                break
            
            # Hash the pattern from tokens1
            pattern = tokens1[start1:start1 + length]
            pattern_hash = self._hash_sequence(pattern)
            
            # Search for this pattern in tokens2
            for j in range(len(tokens2) - length + 1):
                # Skip if any tokens marked
                if any(marked2[j:j + length]):
                    continue
                
                # Hash candidate from tokens2
                candidate = tokens2[j:j + length]
                candidate_hash = self._hash_sequence(candidate)
                
                # If hashes match, verify actual equality
                if pattern_hash == candidate_hash and pattern == candidate:
                    matches.append((j, length))
                    break  # Found match for this length
            
            if matches:
                break  # Greedy: stop at first (longest) match
        
        return matches
    
    def _hash_sequence(self, tokens: list) -> int:
        """Compute Rabin-Karp hash for token sequence"""
        hash_value = 0
        for token in tokens:
            # Simple hash based on token string
            token_hash = hash(token) % self.prime
            hash_value = (hash_value * self.base + token_hash) % self.prime
        return hash_value
    
    def _compute_coverage(self, matches: list, total_length: int, source: int) -> float:
        """Compute what percentage of tokens are covered by matches."""
        if total_length == 0:
            return 0.0
        
        covered = [False] * total_length
        
        for start1, start2, length in matches:
            start = start1 if source == 1 else start2
            for i in range(start, start + length):
                if i < total_length:
                    covered[i] = True
        
        coverage = sum(covered) / total_length
        return coverage

# ============================================================================
# UNIFIED STRUCTURAL SIMILARITY INTERFACE
# ============================================================================

class StructuralSimilarity:
    """
    Unified structural similarity interface supporting both AST and RK-GST.
    """
    
    def __init__(self, method: StructuralMethod = None):
        """
        Initialize structural similarity analyzer.
        
        Args:
            method: Method to use (AST, RKGST, or HYBRID)
        """
        from src.config.weights import DEFAULT_STRUCTURAL_METHOD
        
        self.method = method or DEFAULT_STRUCTURAL_METHOD
        self.ast_analyzer = ASTSimilarityAnalyzer()
        self.rkgst_analyzer = RKGSTSimilarityAnalyzer()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def compute_similarity(self, code1: str, code2: str) -> dict:
        """
        Compute structural similarity using configured method.
        
        Returns:
            {
                'score': float (0-100),
                'method': str,
                'breakdown': dict (if hybrid)
            }
        """
        if self.method == StructuralMethod.AST:
            score = self.ast_analyzer.compute_similarity(code1, code2)
            return {
                'score': score,
                'method': 'ast',
                'breakdown': None
            }
        
        elif self.method == StructuralMethod.RKGST:
            score = self.rkgst_analyzer.compute_similarity(code1, code2)
            return {
                'score': score,
                'method': 'rkgst',
                'breakdown': None
            }
        
        else:  # HYBRID
            ast_score = self.ast_analyzer.compute_similarity(code1, code2)
            rkgst_score = self.rkgst_analyzer.compute_similarity(code1, code2)
            
            # Weighted average
            final_score = (
                ast_score * HYBRID_WEIGHTS['ast'] + 
                rkgst_score * HYBRID_WEIGHTS['rkgst']
            )
            
            return {
                'score': final_score,
                'method': 'hybrid',
                'breakdown': {
                    'ast': ast_score,
                    'rkgst': rkgst_score
                }
            }

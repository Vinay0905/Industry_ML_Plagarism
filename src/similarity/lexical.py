"""
Lexical similarity analyzer using TF-IDF and token-based comparison.
This is a WEAK signal and should only be used as supporting evidence.
"""

import re
import logging
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from src.config.weights import LEXICAL_CONFIG

class LexicalSimilarity:
    """
    Lexical similarity analyzer (weak signal).
    
    Uses TF-IDF vectorization and cosine similarity for fast text comparison.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize lexical similarity analyzer.
        
        Args:
            config: Configuration dictionary (uses defaults if None)
        """
        self.config = config or LEXICAL_CONFIG
        self.logger = logging.getLogger(self.__class__.__name__)
        self.vectorizer = None
    
    def compute_similarity(self, code1: str, code2: str) -> float:
        """
        Compute lexical similarity between two code snippets.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
        
        Returns:
            Similarity score (0-100%)
        """
        # Tokenize both codes
        tokens1 = self._tokenize(code1)
        tokens2 = self._tokenize(code2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        
        try:
            vectors = vectorizer.fit_transform([
                ' '.join(tokens1),
                ' '.join(tokens2)
            ])
            
            # Compute cosine similarity
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            
            return float(similarity * 100)  # Convert to percentage
            
        except Exception as e:
            self.logger.error(f"Error computing lexical similarity: {e}")
            return 0.0
    
    def compute_pairwise_similarities(self, codes: List[str]) -> np.ndarray:
        """
        Compute pairwise lexical similarities for multiple codes.
        
        Args:
            codes: List of code snippets
        
        Returns:
            NxN similarity matrix (percentages)
        """
        if not codes:
            return np.array([])
        
        # Tokenize all codes
        tokenized_codes = [' '.join(self._tokenize(code)) for code in codes]
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        
        try:
            vectors = vectorizer.fit_transform(tokenized_codes)
            
            # Compute pairwise cosine similarities
            similarities = cosine_similarity(vectors)
            
            return similarities * 100  # Convert to percentages
            
        except Exception as e:
            self.logger.error(f"Error computing pairwise similarities: {e}")
            return np.zeros((len(codes), len(codes)))
    
    def _tokenize(self, code: str) -> List[str]:
        """
        Tokenize code into semantic tokens.
        
        Args:
            code: Source code
        
        Returns:
            List of tokens
        """
        # Simple tokenization: extract words, operators, and keywords
        # Pattern matches identifiers, numbers, and operators
        token_pattern = r'\b\w+\b|[+\-*/%=<>!&|^~(){}\[\];,.]'
        tokens = re.findall(token_pattern, code)
        
        # Filter out very short tokens and numbers (optional)
        tokens = [t for t in tokens if len(t) > 1 or t in '(){}[];,']
        
        return tokens
    
    def get_token_statistics(self, code: str) -> Dict:
        """
        Get token statistics for code.
        
        Args:
            code: Source code
        
        Returns:
            Dictionary with token statistics
        """
        tokens = self._tokenize(code)
        
        return {
            'total_tokens': len(tokens),
            'unique_tokens': len(set(tokens)),
            'vocabulary_richness': len(set(tokens)) / len(tokens) if tokens else 0
        }

"""
Score fusion module that combines similarity signals with student-safe bias.
"""

import logging
from typing import Dict, List, Tuple
import numpy as np

from src.config.settings import (
    SIMILARITY_WEIGHTS,
    STUDENT_SAFE_CONFIG,
    SEVERE_THRESHOLD,
    PARTIAL_THRESHOLD
)
from src.similarity.lexical import LexicalSimilarity
from src.similarity.structural import StructuralSimilarity
from src.similarity.semantic import SemanticSimilarity
from src.normalization import get_normalizer

class PlagiarismScorer:
    """
    Combines multiple similarity signals and applies student-safe bias.
    """
    
    def __init__(self):
        """Initialize the plagiarism scorer."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize similarity analyzers
        self.lexical_analyzer = LexicalSimilarity()
        self.structural_analyzer = StructuralSimilarity()
        self.semantic_analyzer = SemanticSimilarity()
    
    def compute_similarity(
        self, 
        code1: str, 
        code2: str,
        language: str = 'python',
        normalize: bool = True
    ) -> Dict:
        """
        Compute comprehensive similarity between two code snippets.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
            language: Programming language
            normalize: Whether to normalize code first
        
        Returns:
            Dictionary with similarity scores and breakdown
        """
        # Normalize code if requested
        if normalize:
            normalizer = get_normalizer(language)
            code1 = normalizer.normalize(code1)
            code2 = normalizer.normalize(code2)
        
        # Compute individual similarities
        lexical_score = self.lexical_analyzer.compute_similarity(code1, code2)
        
        structural_result = self.structural_analyzer.compute_similarity(code1, code2)
        structural_score = structural_result['score']
        
        semantic_score = self.semantic_analyzer.compute_similarity(code1, code2)
        
        # Weighted combination
        raw_score = (
            lexical_score * SIMILARITY_WEIGHTS['lexical'] +
            structural_score * SIMILARITY_WEIGHTS['structural'] +
            semantic_score * SIMILARITY_WEIGHTS['semantic']
        )
        
        # Apply student-safe bias
        final_score, adjustments = self._apply_student_safe_bias(
            lexical_score, structural_score, semantic_score, raw_score
        )
        
        # Classify severity
        severity = self._classify_severity(final_score)
        
        return {
            'final_score': final_score,
            'raw_score': raw_score,
            'breakdown': {
                'lexical': lexical_score,
                'structural': structural_score,
                'semantic': semantic_score
            },
            'structural_method': structural_result['method'],
            'structural_breakdown': structural_result.get('breakdown'),
            'severity': severity,
            'adjustments': adjustments
        }
    
    def _apply_student_safe_bias(
        self,
        lexical: float,
        structural: float,
        semantic: float,
        raw_score: float
    ) -> Tuple[float, List[str]]:
        """
        Apply student-safe bias adjustments.
        
        Returns:
            Tuple of (adjusted_score, list_of_adjustments)
        """
        config = STUDENT_SAFE_CONFIG
        score = raw_score
        adjustments = []
        
        # 1. Penalize if only lexical similarity is high
        if config.get('penalize_lexical_only', True):
            if lexical > 70 and structural < 50 and semantic < 50:
                reduction = config.get('lexical_only_reduction', 0.15) * 100
                score -= reduction
                adjustments.append(f"Reduced by {reduction:.1f}% (lexical-only similarity)")
        
        # 2. Boost if structural and semantic agree
        if config.get('boost_multi_signal_agreement', True):
            threshold = config.get('agreement_threshold', 0.85) * 100
            if structural >= threshold and semantic >= threshold:
                boost = config.get('agreement_boost', 0.05) * 100
                score += boost
                adjustments.append(f"Boosted by {boost:.1f}% (multi-signal agreement)")
        
        # 3. Reduce if signals are uncertain (high variance)
        if config.get('uncertainty_threshold', 5.0):
            scores = [lexical, structural, semantic]
            variance = np.std(scores)
            if variance > config['uncertainty_threshold']:
                penalty = config.get('uncertainty_penalty', 0.10) * 100
                score -= penalty
                adjustments.append(f"Reduced by {penalty:.1f}% (signal uncertainty)")
        
        # Ensure score is in valid range
        score = max(0.0, min(100.0, score))
        
        return score, adjustments
    
    def _classify_severity(self, score: float) -> str:
        """
        Classify plagiarism severity based on score.
        
        Args:
            score: Final similarity score (0-100)
        
        Returns:
            Severity level: 'severe', 'partial', or 'clean'
        """
        if score >= SEVERE_THRESHOLD:
            return 'severe'
        elif score >= PARTIAL_THRESHOLD:
            return 'partial'
        else:
            return 'clean'
    
    def analyze_all(
        self,
        submissions: List[Dict],
        normalize: bool = True
    ) -> List[Dict]:
        """
        Analyze all submissions and find most similar pairs.
        
        Args:
            submissions: List of submission dictionaries
            normalize: Whether to normalize code
        
        Returns:
            List of results for each submission
        """
        from tqdm import tqdm
        
        n = len(submissions)
        results = []
        
        # Get language (assume all same)
        language = submissions[0].get('language', 'python')
        
        self.logger.info(f"Analyzing {n} submissions (pairwise comparisons: {n*(n-1)//2})")
        
        # For each submission, find most similar
        for i, sub in enumerate(tqdm(submissions, desc="Analyzing submissions")):
            max_similarity = 0.0
            most_similar_id = None
            best_result = None
            
            # Compare with all others
            for j, other in enumerate(submissions):
                if i == j:
                    continue
                
                result = self.compute_similarity(
                    sub['code'],
                    other['code'],
                    language=language,
                    normalize=normalize
                )
                
                if result['final_score'] > max_similarity:
                    max_similarity = result['final_score']
                    most_similar_id = other['submission_id']
                    best_result = result
            
            # Store result for this submission
            results.append({
                'submission_id': sub['submission_id'],
                'similarity_score': max_similarity,
                'most_similar_to': most_similar_id,
                'breakdown': best_result['breakdown'] if best_result else {},
                'severity': best_result['severity'] if best_result else 'clean',
                'adjustments': best_result['adjustments'] if best_result else []
            })
        
        return results

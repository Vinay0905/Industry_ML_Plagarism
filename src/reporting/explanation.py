"""
Report explanation generator with adaptive depth.
Converts scores into academic,human-readable explanations.
"""

import logging
from typing import Dict, List

from src.config.settings import (
    DEEP_EXPLANATION_THRESHOLD,
    SEVERE_THRESHOLD,
    PARTIAL_THRESHOLD
)
from src.utils.helpers import detect_algorithm_complexity

class ExplanationGenerator:
    """
    Generates human-readable explanations for plagiarism reports.
    """
    
    def __init__(self):
        """Initialize the explanation generator."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_report(
        self,
        submission_id: str,
        similarity_score: float,
        breakdown: Dict[str, float],
        severity: str,
        most_similar_to: str = None,
        code: str = None,
        adjustments: List[str] = None
    ) -> Dict:
        """
        Generate complete plagiarism report for a submission.
        
        Args:
            submission_id: ID of the submission
            similarity_score: Final similarity score (0-100)
            breakdown: Breakdown of similarity signals
            severity: Severity classification
            most_similar_to: ID of most similar submission
            code: Original code (for complexity detection)
            adjustments: List of student-safe bias adjustments
        
        Returns:
            Complete report dictionary
        """
        # Determine explanation depth
        is_complex = False
        if code:
            complexity = detect_algorithm_complexity(code)
            is_complex = (complexity == 'complex')
        
        use_deep_explanation = (
            similarity_score >= DEEP_EXPLANATION_THRESHOLD or
            is_complex
        )
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            similarity_score,
            breakdown,
            severity,
            depth='deep' if use_deep_explanation else 'medium'
        )
        
        # Generate penalty decision
        penalty_decision = self._generate_penalty_decision(
            similarity_score,
            severity,
            breakdown
        )
        
        # Build report
        report = {
            'submission_id': submission_id,
            'similarity_score': f"{similarity_score:.1f}%",
            'most_similar_to': most_similar_to or "N/A",
            'breakdown': {
                'lexical_similarity': f"{breakdown.get('lexical', 0):.1f}%",
                'structural_similarity': f"{breakdown.get('structural', 0):.1f}%",
                'semantic_similarity': f"{breakdown.get('semantic', 0):.1f}%"
            },
            'interpretation': interpretation,
            'penalty_decision': penalty_decision,
            'severity': severity,
            'adjustments': adjustments or []
        }
        
        return report
    
    def _generate_interpretation(
        self,
        score: float,
        breakdown: Dict[str, float],
        severity: str,
        depth: str = 'medium'
    ) -> str:
        """
        Generate interpretation of similarity scores.
        
        Args:
            score: Final similarity score
            breakdown: Similarity signal breakdown
            severity: Severity classification
            depth: 'medium' or 'deep'
        
        Returns:
            Interpretation string
        """
        lexical = breakdown.get('lexical', 0)
        structural = breakdown.get('structural', 0)
        semantic = breakdown.get('semantic', 0)
        
        interpretation_parts = []
        
        # Overall assessment
        if severity == 'severe':
            interpretation_parts.append(
                "**High-confidence plagiarism detected.** "
                "Near-identical logic and algorithmic structure observed."
            )
        elif severity == 'partial':
            interpretation_parts.append(
                "**Partial similarity detected.** "
                "Core logic shows significant overlap with cosmetic changes."
            )
        else:
            interpretation_parts.append(
                "**Original work.** "
                "No significant plagiarism indicators found."
            )
        
        # Breakdown analysis
        if depth == 'deep':
            # Detailed analysis
            if structural > 70:
                interpretation_parts.append(
                    f"Structural similarity ({structural:.1f}%) indicates "
                    "matching control-flow patterns and algorithmic structure. "
                    "This suggests the underlying logic is nearly identical."
                )
            
            if semantic > 70:
                interpretation_parts.append(
                    f"Semantic similarity ({semantic:.1f}%) reveals "
                    "matching algorithmic intent and data-flow patterns. "
                    "Both codes solve the problem using the same approach."
                )
            
            if lexical > 70 and structural > 70:
                interpretation_parts.append(
                    "High lexical + structural similarity indicates "
                    "likely copy-paste with minimal refactoring."
                )
            elif structural > 70 and lexical < 50:
                interpretation_parts.append(
                    "Structural similarity without lexical similarity suggests "
                    "the code was refactored (renamed variables, reformatted) "
                    "but the core logic remains identical."
                )
            
            # Check for cosmetic changes
            if lexical < 50 and (structural > 60 or semantic > 60):
                interpretation_parts.append(
                    "Despite superficial differences in naming and formatting, "
                    "the algorithmic structure is substantially similar."
                )
        
        else:
            # Medium depth
            if lexical > 70:
                interpretation_parts.append(
                    f"Lexical similarity ({lexical:.1f}%) shows text-level overlap."
                )
            
            if structural > 70:
                interpretation_parts.append(
                    f"Structural similarity ({structural:.1f}%) shows matching logic patterns."
                )
            
            if semantic > 70:
                interpretation_parts.append(
                    f"Semantic similarity ({semantic:.1f}%) shows matching algorithmic intent."
                )
        
        return " ".join(interpretation_parts)
    
    def _generate_penalty_decision(
        self,
        score: float,
        severity: str,
        breakdown: Dict[str, float]
    ) -> str:
        """
        Generate recommended penalty decision.
        
        Args:
            score: Final similarity score
            severity: Severity classification
            breakdown: Similarity signal breakdown
        
        Returns:
            Penalty decision string
        """
        if severity == 'severe':
            return "**Severe plagiarism** - Recommend zero credit and academic integrity review"
        
        elif severity == 'partial':
            structural = breakdown.get('structural', 0)
            semantic = breakdown.get('semantic', 0)
            
            if structural > 75 or semantic > 75:
                return "**Moderate deduction** - Substantial similarity detected, recommend 50-70% deduction"
            else:
                return "**Minor deduction** - Some similarity detected, recommend 20-30% deduction or warning"
        
        else:
            return "**No penalty** - Work appears original"
    
    def format_text_report(self, report: Dict) -> str:
        """
        Format report as plain text.
        
        Args:
            report: Report dictionary
        
        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"PLAGIARISM ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Submission ID: {report['submission_id']}")
        lines.append(f"Most Similar To: {report['most_similar_to']}")
        lines.append("")
        
        lines.append(f"Similarity Score: {report['similarity_score']}")
        lines.append("")
        
        lines.append("Breakdown:")
        for key, value in report['breakdown'].items():
            lines.append(f"  - {key.replace('_', ' ').title()}: {value}")
        lines.append("")
        
        lines.append("Interpretation:")
        lines.append(report['interpretation'])
        lines.append("")
        
        lines.append("Penalty Decision:")
        lines.append(report['penalty_decision'])
        lines.append("")
        
        if report.get('adjustments'):
            lines.append("Student-Safe Adjustments Applied:")
            for adj in report['adjustments']:
                lines.append(f"  - {adj}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)

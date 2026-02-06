"""Main src package initialization."""

__version__ = '0.1.0'
__author__ = 'Academic Plagiarism Detection Team'

# Make key classes easily importable
from src.io import load_submissions, validate_submissions
from src.normalization import get_normalizer
from src.similarity import (
    LexicalSimilarity,
    StructuralSimilarity,
    SemanticSimilarity
)
from src.fusion import PlagiarismScorer
from src.reporting import ExplanationGenerator

__all__ = [
    'load_submissions',
    'validate_submissions',
    'get_normalizer',
    'LexicalSimilarity',
    'StructuralSimilarity',
    'SemanticSimilarity',
    'PlagiarismScorer',
    'ExplanationGenerator'
]

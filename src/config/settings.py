"""
Global configuration settings for the plagiarism detection system.
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DIR = DATA_DIR / "results"

# ============================================================================
# PLAGIARISM THRESHOLDS
# ============================================================================

# Severity classification thresholds (as specified in requirements)
SEVERE_THRESHOLD = 90.0     # >= 90% is severe plagiarism
PARTIAL_THRESHOLD = 60.0    # 60-89% is partial plagiarism
                            # < 60% is considered clean

# ============================================================================
# SIMILARITY SIGNAL CONFIGURATION
# ============================================================================

# Default weights for combining similarity signals
# These weights determine how much each signal contributes to final score
SIMILARITY_WEIGHTS = {
    'lexical': 0.15,      # Weak signal (supporting evidence only)
    'structural': 0.45,   # Strong signal (primary detector)
    'semantic': 0.40      # Strong signal (algorithmic intent)
}

# Ensure weights sum to 1.0
assert abs(sum(SIMILARITY_WEIGHTS.values()) - 1.0) < 0.01, "Weights must sum to 1.0"

# ============================================================================
# STUDENT-SAFE BIAS CONFIGURATION
# ============================================================================

# Adjustments to favor false negatives over false positives
STUDENT_SAFE_CONFIG = {
    # Reduce score if only lexical similarity is high
    'penalize_lexical_only': True,
    'lexical_only_reduction': 0.15,  # Reduce by 15 percentage points
    
    # Increase confidence when structural + semantic agree
    'boost_multi_signal_agreement': True,
    'agreement_threshold': 0.85,  # If both > 85%, boost confidence
    'agreement_boost': 0.05,  # Boost by 5 percentage points
    
    # When uncertain, err toward leniency
    'uncertainty_threshold': 5.0,  # If signals differ by > 5%, apply penalty
    'uncertainty_penalty': 0.10,  # Reduce by 10 percentage points
}

# ============================================================================
# ADAPTIVE EXPLANATION DEPTH
# ============================================================================

# When to switch from medium to deep explanation
DEEP_EXPLANATION_THRESHOLD = 70.0  # >= 70% similarity triggers deep explanation
COMPLEX_ALGORITHM_KEYWORDS = [
    'dynamic_programming', 'recursion', 'graph', 'tree', 'sorting',
    'search', 'optimization', 'backtracking', 'divide_conquer'
]

# ============================================================================
# INPUT/OUTPUT CONFIGURATION
# ============================================================================

# Supported input formats
SUPPORTED_INPUT_FORMATS = ['csv', 'json']

# Required fields in input data
REQUIRED_FIELDS = ['submission_id', 'code']
OPTIONAL_FIELDS = ['language', 'student_id', 'timestamp', 'metadata']

# Output format
OUTPUT_FORMAT = 'json'  # Options: 'json', 'csv', 'html'

# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

# Supported programming languages
SUPPORTED_LANGUAGES = ['python', 'cpp', 'java']

# Language detection patterns (simple heuristics)
LANGUAGE_PATTERNS = {
    'python': ['.py', 'def ', 'import ', 'class '],
    'cpp': ['.cpp', '.h', '#include', 'std::', 'cout'],
    'java': ['.java', 'public class', 'public static void main', 'System.out']
}

# ============================================================================
# NORMALIZATION SETTINGS
# ============================================================================

NORMALIZATION_CONFIG = {
    'remove_comments': True,
    'remove_docstrings': True,
    'normalize_whitespace': True,
    'normalize_identifiers': True,  # Rename vars to var_1, var_2, etc.
    'canonicalize_control_flow': True,
    'preserve_structure': True
}

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = PROJECT_ROOT / 'plagiarism_detector.log'

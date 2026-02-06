"""
Helper utility functions for the plagiarism detection system.
"""

import hashlib
import logging
from typing import List, Any
from pathlib import Path

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_level: str = 'INFO', log_file: Path = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(log_file)] if log_file else [])
        ]
    )

# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

def detect_language(code: str, filename: str = None) -> str:
    """
    Detect programming language from code or filename.
    
    Args:
        code: Source code string
        filename: Optional filename with extension
    
    Returns:
        Detected language ('python', 'cpp', 'java') or 'unknown'
    """
    from src.config.settings import LANGUAGE_PATTERNS
    
    # Check filename extension first
    if filename:
        if filename.endswith('.py'):
            return 'python'
        elif filename.endswith(('.cpp', '.cc', '.h', '.hpp')):
            return 'cpp'
        elif filename.endswith('.java'):
            return 'java'
    
    # Check code patterns
    code_lower = code.lower()
    
    python_score = sum(1 for pattern in LANGUAGE_PATTERNS['python'] 
                      if pattern in code_lower)
    cpp_score = sum(1 for pattern in LANGUAGE_PATTERNS['cpp'] 
                   if pattern in code_lower)
    java_score = sum(1 for pattern in LANGUAGE_PATTERNS['java'] 
                    if pattern in code_lower)
    
    scores = {'python': python_score, 'cpp': cpp_score, 'java': java_score}
    max_lang = max(scores, key=scores.get)
    
    if scores[max_lang] == 0:
        return 'unknown'
    
    return max_lang

# ============================================================================
# HASHING AND FINGERPRINTING
# ============================================================================

def compute_hash(text: str) -> str:
    """
    Compute SHA-256 hash of text.
    
    Args:
        text: Input text
    
    Returns:
        Hex digest of hash
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def create_fingerprint(code: str) -> dict:
    """
    Create a quick fingerprint of code for caching.
    
    Args:
        code: Source code
    
    Returns:
        Dict with fingerprint metadata
    """
    return {
        'hash': compute_hash(code),
        'length': len(code),
        'line_count': code.count('\n') + 1
    }

# ============================================================================
# PROGRESS TRACKING
# ============================================================================

def pairwise_comparison_count(n_submissions: int) -> int:
    """
    Calculate number of pairwise comparisons needed.
    
    Args:
        n_submissions: Number of submissions
    
    Returns:
        Number of comparisons (n choose 2)
    """
    return n_submissions * (n_submissions - 1) // 2

# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_fields(data: dict, required_fields: List[str], optional_fields: List[str] = None) -> bool:
    """
    Validate that data contains required fields.
    
    Args:
        data: Data dictionary
        required_fields: List of required field names
        optional_fields: List of optional field names
    
    Returns:
        True if valid, False otherwise
    """
    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return False
    
    return True

# ============================================================================
# TEXT PROCESSING
# ============================================================================

def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Input text
    
    Returns:
        Text with normalized whitespace
    """
    import re
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove trailing whitespace
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    # Remove multiple blank lines
    text = re.sub(r'\n\n+', '\n\n', text)
    return text.strip()

# ============================================================================
# ALGORITHM DETECTION
# ============================================================================

def detect_algorithm_complexity(code: str) -> str:
    """
    Detect if code contains complex algorithms (for adaptive explanation).
    
    Args:
        code: Source code
    
    Returns:
        'simple', 'moderate', or 'complex'
    """
    from src.config.settings import COMPLEX_ALGORITHM_KEYWORDS
    
    code_lower = code.lower()
    
    # Count occurrences of complex algorithm keywords
    complexity_score = 0
    
    # Check for recursion
    if 'def ' in code_lower and code_lower.count('def ') > 2:
        complexity_score += 1
    
    # Check for nested loops
    loop_count = code_lower.count('for ') + code_lower.count('while ')
    if loop_count > 2:
        complexity_score += 1
    
    # Check for data structures
    if any(keyword in code_lower for keyword in ['dict', 'list', 'set', 'tree', 'graph']):
        complexity_score += 1
    
    # Check for dynamic programming patterns
    if 'memo' in code_lower or 'dp[' in code_lower or 'cache' in code_lower:
        complexity_score += 2
    
    if complexity_score >= 3:
        return 'complex'
    elif complexity_score >= 1:
        return 'moderate'
    else:
        return 'simple'

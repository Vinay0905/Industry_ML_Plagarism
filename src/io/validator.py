"""
Validator for submission data.
Ensures all submissions are valid and compatible for plagiarism detection.
"""

import logging
from typing import List, Dict, Any

from src.config.settings import (
    REQUIRED_FIELDS, 
    OPTIONAL_FIELDS,
    SUPPORTED_LANGUAGES
)

logger = logging.getLogger(__name__)

class SubmissionValidator:
    """
    Validates submission data for plagiarism detection.
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, raise exceptions on validation errors
        """
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate(self, submissions: List[Dict[str, Any]]) -> tuple:
        """
        Validate all submissions.
        
        Args:
            submissions: List of submission dictionaries
        
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        
        Raises:
            ValueError: If strict_mode=True and validation fails
        """
        errors = []
        
        # Check minimum submissions
        if len(submissions) < 2:
            errors.append("Need at least 2 submissions for comparison")
        
        # Check required fields
        field_errors = self._validate_required_fields(submissions)
        errors.extend(field_errors)
        
        # Check language consistency
        lang_errors = self._validate_language_consistency(submissions)
        errors.extend(lang_errors)
        
        # Check for empty code
        empty_errors = self._validate_non_empty_code(submissions)
        errors.extend(empty_errors)
        
        # Check for duplicate IDs
        dup_errors = self._validate_unique_ids(submissions)
        errors.extend(dup_errors)
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.logger.error(f"Validation failed with {len(errors)} errors")
            for error in errors:
                self.logger.error(f"  - {error}")
            
            if self.strict_mode:
                raise ValueError(f"Validation failed:\n" + "\n".join(errors))
        
        return is_valid, errors
    
    def _validate_required_fields(self, submissions: List[Dict[str, Any]]) -> List[str]:
        """Check that all required fields are present."""
        errors = []
        
        for i, sub in enumerate(submissions):
            for field in REQUIRED_FIELDS:
                if field not in sub or sub[field] is None:
                    errors.append(
                        f"Submission {i} missing required field '{field}'"
                    )
        
        return errors
    
    def _validate_language_consistency(self, submissions: List[Dict[str, Any]]) -> List[str]:
        """
        Validate that all submissions use the same programming language.
        CRITICAL: Cross-language plagiarism is NOT supported.
        """
        errors = []
        
        languages = set()
        for sub in submissions:
            lang = sub.get('language', 'unknown')
            languages.add(lang)
        
        if len(languages) > 1:
            errors.append(
                f"Multiple languages detected: {languages}. "
                f"All submissions must be in the SAME language."
            )
        elif len(languages) == 1:
            lang = list(languages)[0]
            if lang not in SUPPORTED_LANGUAGES and lang != 'unknown':
                errors.append(
                    f"Unsupported language: {lang}. "
                    f"Supported: {SUPPORTED_LANGUAGES}"
                )
        
        return errors
    
    def _validate_non_empty_code(self, submissions: List[Dict[str, Any]]) -> List[str]:
        """Check that code fields are not empty."""
        errors = []
        
        for sub in submissions:
            code = sub.get('code', '')
            if not code or not code.strip():
                errors.append(
                    f"Submission '{sub.get('submission_id')}' has empty code"
                )
        
        return errors
    
    def _validate_unique_ids(self, submissions: List[Dict[str, Any]]) -> List[str]:
        """Check for duplicate submission IDs."""
        errors = []
        
        ids = [sub.get('submission_id') for sub in submissions]
        unique_ids = set(ids)
        
        if len(ids) != len(unique_ids):
            duplicates = [id for id in ids if ids.count(id) > 1]
            errors.append(
                f"Duplicate submission IDs found: {set(duplicates)}"
            )
        
        return errors
    
    def get_statistics(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about submissions.
        
        Args:
            submissions: List of submission dictionaries
        
        Returns:
            Dictionary with statistics
        """
        if not submissions:
            return {}
        
        languages = [sub.get('language', 'unknown') for sub in submissions]
        code_lengths = [len(sub.get('code', '')) for sub in submissions]
        
        stats = {
            'total_submissions': len(submissions),
            'languages': list(set(languages)),
            'avg_code_length': sum(code_lengths) / len(code_lengths),
            'min_code_length': min(code_lengths),
            'max_code_length': max(code_lengths),
            'total_comparisons': len(submissions) * (len(submissions) - 1) // 2
        }
        
        return stats

# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def validate_submissions(submissions: List[Dict[str, Any]], 
                        strict: bool = True) -> tuple:
    """
    Convenience function to validate submissions.
    
    Args:
        submissions: List of submission dictionaries
        strict: If True, raise exception on validation errors
    
    Returns:
        Tuple of (is_valid: bool, errors: List[str])
    
    Example:
        >>> is_valid, errors = validate_submissions(submissions)
        >>> if not is_valid:
        ...     print(f"Validation errors: {errors}")
    """
    validator = SubmissionValidator(strict_mode=strict)
    return validator.validate(submissions)

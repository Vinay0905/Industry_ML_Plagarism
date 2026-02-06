"""
Data loader for plagiarism detection system.
Handles loading submissions from CSV and JSON formats.
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Union

from src.config.settings import SUPPORTED_INPUT_FORMATS, REQUIRED_FIELDS
from src.utils.helpers import detect_language, setup_logging

# Setup logging
logger = logging.getLogger(__name__)

class SubmissionLoader:
    """
    Loader for code submissions from various formats.
    """
    
    def __init__(self):
        """Initialize the submission loader."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load(self, filepath: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load submissions from file (CSV or JSON).
        
        Args:
            filepath: Path to input file
        
        Returns:
            List of submission dictionaries
        
        Raises:
            ValueError: If file format not supported
            FileNotFoundError: If file doesn't exist
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Input file not found: {filepath}")
        
        # Detect format from extension
        file_ext = filepath.suffix.lower().lstrip('.')
        
        if file_ext not in SUPPORTED_INPUT_FORMATS:
            raise ValueError(
                f"Unsupported format: {file_ext}. "
                f"Supported formats: {SUPPORTED_INPUT_FORMATS}"
            )
        
        self.logger.info(f"Loading submissions from {filepath}")
        
        if file_ext == 'csv':
            submissions = self._load_csv(filepath)
        elif file_ext == 'json':
            submissions = self._load_json(filepath)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
        
        self.logger.info(f"Loaded {len(submissions)} submissions")
        
        # Auto-detect language if not provided
        submissions = self._auto_detect_languages(submissions)
        
        return submissions
    
    def _load_csv(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Load submissions from CSV file.
        
        Flexible column mapping:
        - 'id' or 'submission_id' for submission identifier
        - 'code' for code content
        - 'language' for programming language (optional)
        - Other columns (userId, problemTitle, etc.) are preserved
        
        Args:
            filepath: Path to CSV file
        
        Returns:
            List of submission dictionaries
        """
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        # Check for identifier column (accept 'id' or 'submission_id')
        if 'submission_id' not in df.columns and 'id' not in df.columns:
            raise ValueError("CSV must contain 'submission_id' or 'id' column")
        
        # Check for code column
        if 'code' not in df.columns:
            raise ValueError(f"CSV must contain 'code' column. Found columns: {list(df.columns)}")
        
        # Rename 'id' to 'submission_id' if needed
        if 'id' in df.columns and 'submission_id' not in df.columns:
            df['submission_id'] = df['id']
            self.logger.info("Mapped 'id' column to 'submission_id'")
        
        # Convert to list of dictionaries
        submissions = df.to_dict('records')
        
        return submissions

    
    def _load_json(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Load submissions from JSON file.
        
        Expected format:
        {
            "submissions": [
                {
                    "submission_id": "s001",
                    "code": "...",
                    "language": "python"
                },
                ...
            ]
        }
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            List of submission dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}")
        
        # Handle both formats: list directly or {"submissions": [...]}
        if isinstance(data, list):
            submissions = data
        elif isinstance(data, dict) and 'submissions' in data:
            submissions = data['submissions']
        else:
            raise ValueError(
                "JSON must be a list or dict with 'submissions' key"
            )
        
        return submissions
    
    def _auto_detect_languages(self, submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Auto-detect programming language if not provided.
        
        Args:
            submissions: List of submission dictionaries
        
        Returns:
            Submissions with language field populated
        """
        for sub in submissions:
            if 'language' not in sub or not sub['language']:
                # Auto-detect from code
                detected_lang = detect_language(
                    sub.get('code', ''),
                    sub.get('filename', None)
                )
                sub['language'] = detected_lang
                self.logger.debug(
                    f"Auto-detected language '{detected_lang}' "
                    f"for submission {sub.get('submission_id')}"
                )
        
        return submissions

# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def load_submissions(filepath: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Convenience function to load submissions.
    
    Args:
        filepath: Path to input file (CSV or JSON)
    
    Returns:
        List of submission dictionaries
    
    Example:
        >>> submissions = load_submissions('data/raw/submissions.csv')
        >>> print(f"Loaded {len(submissions)} submissions")
    """
    loader = SubmissionLoader()
    return loader.load(filepath)

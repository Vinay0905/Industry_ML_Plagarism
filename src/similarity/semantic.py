"""
Semantic similarity analyzer using ML-based embeddings.
This is a STRONG signal for detecting algorithmic intent.
"""

import logging
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

# Optional: Try to import transformers for CodeBERT
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from src.config.weights import SEMANTIC_CONFIG

class SemanticSimilarity:
    """
    Semantic similarity using code embeddings.
    Falls back to lexical similarity if transformers not available.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize semantic similarity analyzer.
        
        Args:
            config: Configuration dictionary (uses defaults if None)
        """
        self.config = config or SEMANTIC_CONFIG
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.model = None
        self.tokenizer = None
        
        # Try to load model if transformers available
        if TRANSFORMERS_AVAILABLE and self.config.get('model') == 'codebert':
            self._load_codebert_model()
        else:
            self.logger.warning(
                "Transformers not available or model not CodeBERT. "
                "Using fallback lexical similarity."
            )
    
    def _load_codebert_model(self):
        """Load CodeBERT model and tokenizer."""
        try:
            model_name = self.config.get('model_name', 'microsoft/codebert-base')
            self.logger.info(f"Loading model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            
            # Move to GPU if available and configured
            if self.config.get('use_gpu', False) and torch.cuda.is_available():
                self.model = self.model.cuda()
                self.logger.info("Using GPU for semantic similarity")
            else:
                self.logger.info("Using CPU for semantic similarity")
            
            self.model.eval()  # Set to evaluation mode
            
        except Exception as e:
            self.logger.error(f"Failed to load CodeBERT model: {e}")
            self.model = None
            self.tokenizer = None
    
    def compute_similarity(self, code1: str, code2: str) -> float:
        """
        Compute semantic similarity between two code snippets.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
        
        Returns:
            Similarity score (0-100%)
        """
        if self.model is not None and self.tokenizer is not None:
            return self._compute_embedding_similarity(code1, code2)
        elif self.config.get('fallback_to_lexical', True):
            return self._fallback_lexical_similarity(code1, code2)
        else:
            self.logger.error("No model available and fallback disabled")
            return 0.0
    
    def _compute_embedding_similarity(self, code1: str, code2: str) -> float:
        """Compute similarity using code embeddings."""
        try:
            # Generate embeddings
            emb1 = self._get_code_embedding(code1)
            emb2 = self._get_code_embedding(code2)
            
            # Compute cosine similarity
            similarity = cosine_similarity(
                emb1.reshape(1, -1),
                emb2.reshape(1, -1)
            )[0][0]
            
            return float(similarity * 100)  # Convert to percentage
            
        except Exception as e:
            self.logger.error(f"Error computing embedding similarity: {e}")
            return 0.0
    
    def _get_code_embedding(self, code: str) -> np.ndarray:
        """
        Get embedding for code snippet.
        
        Args:
            code: Source code
        
        Returns:
            Embedding vector
        """
        # Tokenize
        max_length = self.config.get('max_length', 512)
        inputs = self.tokenizer(
            code,
            return_tensors='pt',
            max_length=max_length,
            truncation=True,
            padding='max_length'
        )
        
        # Move to GPU if needed
        if self.config.get('use_gpu', False) and torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embedding
            embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
        
        return embedding
    
    def _fallback_lexical_similarity(self, code1: str, code2: str) -> float:
        """
        Fallback to simple lexical similarity if model not available.
        
        Args:
            code1: First code snippet
            code2: Second code snippet
        
        Returns:
            Similarity score (0-100%)
        """
        from src.similarity.lexical import LexicalSimilarity
        
        lexical_analyzer = LexicalSimilarity()
        return lexical_analyzer.compute_similarity(code1, code2)
    
    def get_batch_embeddings(self, codes: List[str]) -> np.ndarray:
        """
        Get embeddings for multiple code snippets.
        
        Args:
            codes: List of code snippets
        
        Returns:
            Array of embeddings (n_codes x embedding_dim)
        """
        if self.model is None or self.tokenizer is None:
            self.logger.error("Model not available for batch embeddings")
            return np.array([])
        
        embeddings = []
        batch_size = self.config.get('batch_size', 16)
        
        # Process in batches
        for i in range(0, len(codes), batch_size):
            batch = codes[i:i + batch_size]
            batch_embeddings = [self._get_code_embedding(code) for code in batch]
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)

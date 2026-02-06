"""
Configurable weights for structural similarity analysis.
Allows fine-tuning of AST and RK-GST approaches.
"""

from enum import Enum

# ============================================================================
# STRUCTURAL SIMILARITY METHOD SELECTION
# ============================================================================

class StructuralMethod(Enum):
    """Available structural similarity methods"""
    TREESITTER = "treesitter"  # Tree-sitter AST (multi-language, robust) - RECOMMENDED
    AST = "ast"                # Python AST only (deep analysis)
    RKGST = "rkgst"            # Rabin-Karp Greedy String Tiling
    HYBRID = "hybrid"          # Combination of methods

# Default method (recommended: TREESITTER for multi-language + robustness)
DEFAULT_STRUCTURAL_METHOD = StructuralMethod.TREESITTER

# ============================================================================
# HYBRID MODE WEIGHTS
# ============================================================================

# When using HYBRID mode, combine Tree-Sitter, AST, and RK-GST with these weights
HYBRID_WEIGHTS = {
    'treesitter': 0.4,  # Tree-sitter gets 40% weight (multi-language, robust)
    'ast': 0.3,         # AST gets 30% weight (Python-specific deep analysis)
    'rkgst': 0.3        # RK-GST gets 30% weight (copy-paste detection)
}

assert abs(sum(HYBRID_WEIGHTS.values()) - 1.0) < 0.01, "Hybrid weights must sum to 1.0"

# ============================================================================
# AST-BASED SIMILARITY WEIGHTS
# ============================================================================

# When using AST method, weight different structural features
AST_FEATURE_WEIGHTS = {
    'tree_structure': 0.40,    # Overall AST shape and node types
    'control_flow': 0.30,      # If/while/for patterns
    'function_calls': 0.20,    # Function call sequences
    'data_flow': 0.10          # Variable dependencies (simplified)
}

assert abs(sum(AST_FEATURE_WEIGHTS.values()) - 1.0) < 0.01, "AST weights must sum to 1.0"

# ============================================================================
# RK-GST CONFIGURATION
# ============================================================================

# Rabin-Karp Greedy String Tiling parameters
RKGST_CONFIG = {
    'min_match_length': 3,     # Minimum token sequence length to consider a match
    'hash_base': 256,          # Base for Rabin-Karp rolling hash
    'hash_prime': 101,         # Prime modulus for hash computation
    'coverage_metric': 'symmetric'  # Options: 'symmetric', 'max', 'min'
}

# ============================================================================
# LEXICAL SIMILARITY CONFIGURATION
# ============================================================================

LEXICAL_CONFIG = {
    'method': 'tfidf',         # Options: 'tfidf', 'jaccard', 'cosine'
    'tokenization': 'word',    # Options: 'word', 'char', 'ngram'
    'ngram_size': 3,           # For n-gram tokenization
    'min_df': 1,               # Minimum document frequency for TF-IDF
    'max_df': 1.0,             # Maximum document frequency for TF-IDF
    'use_idf': True            # Whether to use inverse document frequency
}

# ============================================================================
# SEMANTIC SIMILARITY CONFIGURATION
# ============================================================================

SEMANTIC_CONFIG = {
    'model': 'codebert',       # Options: 'codebert', 'graphcodebert', 'unixcoder'
    'model_name': 'microsoft/codebert-base',  # HuggingFace model name
    'embedding_dim': 768,      # Embedding dimension
    'similarity_metric': 'cosine',  # Options: 'cosine', 'euclidean'
    'batch_size': 16,          # Batch size for encoding
    'max_length': 512,         # Maximum token length for transformer
    'use_gpu': False,          # Set to True if GPU available
    'fallback_to_lexical': True  # If model fails, use lexical similarity
}

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

OPTIMIZATION_CONFIG = {
    'enable_caching': True,     # Cache normalized code and embeddings
    'parallel_processing': True,  # Use multiprocessing for pairwise comparisons
    'num_workers': 4,           # Number of worker processes
    'chunk_size': 100           # Chunk size for parallel processing
}

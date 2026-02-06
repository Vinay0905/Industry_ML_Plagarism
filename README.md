# Academic Code Plagiarism Detection System

An industrial-grade plagiarism detection pipeline for college programming assignments, designed with a **student-safe** philosophy.

## 🎯 Philosophy

This system prioritizes fairness and accuracy:

- **Student-Safe**: False positives are worse than false negatives
- **Multi-Signal Analysis**: Never rely on a single similarity metric
- **Explainable**: All decisions are transparent and defensible
- **Deterministic**: Consistent, reproducible results

## 📊 Features

### Three-Signal Detection System

1. **Lexical Similarity** (15% weight) - Fast text-based comparison
2. **Structural Similarity** (45% weight) - AST and RK-GST analysis
3. **Semantic Similarity** (40% weight) - ML-based algorithmic intent

### Severity Classification

- **≥ 90%** → Severe plagiarism (near-exact logic copying)
- **60-89%** → Partial plagiarism (core logic copied with disguises)
- **< 60%** → Clean (original work)

### Supported Languages

- Python
- C++
- Java

## 🏗️ Project Structure

```
plagiarism-checker/
│
├── data/
│   ├── raw/              # Input CSV/JSON files
│   ├── processed/        # Normalized, tokenized data
│   └── results/          # Similarity reports
│
├── notebooks/            # Jupyter notebooks for testing
│   ├── 00_data_loading.ipynb
│   ├── 01_normalization.ipynb
│   ├── 02_lexical_similarity.ipynb
│   ├── 03_ast_similarity.ipynb        # AST vs RK-GST comparison
│   ├── 04_semantic_similarity.ipynb
│   ├── 05_score_fusion_and_report.ipynb
│   └── 99_end_to_end_demo.ipynb
│
├── src/                  # Core implementation
│   ├── config/          # Configuration files
│   ├── io/              # Data loading and validation
│   ├── normalization/   # Code normalization (Python, C++, Java)
│   ├── similarity/      # Similarity analyzers
│   ├── fusion/          # Score fusion logic
│   ├── reporting/       # Report generation
│   └── utils/           # Helper functions
│
├── requirements.txt
└── README.md

```

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from src.io.loader import load_submissions
from src.fusion.scorer import PlagiarismScorer

# Load submissions
submissions = load_submissions('data/raw/submissions.csv')

# Analyze similarity (uses token-based normalization by default)
scorer = PlagiarismScorer()
results = scorer.analyze_all(submissions)

# View report
for result in results:
    print(f"Submission {result['submission_id']}: {result['similarity_score']:.1f}% similarity")
    print(f"  Severity: {result['severity']}")
```

## 🔧 Code Normalization

The system supports **multiple normalization approaches**:

### Token-Based Normalization (Default ⭐ Recommended)

**Universal, fast, language-agnostic approach**

```python
from src.normalization import get_normalizer

# Token-based normalizer (default - works for Python, C++, Java, etc.)
normalizer = get_normalizer('python')  # method='token' is default
normalized_code = normalizer.normalize(code)
```

**Features:**

- ✅ Works across multiple languages (Python, C++, Java)
- ✅ Fast regex-based tokenization
- ✅ Removes comments
- ✅ Normalizes identifiers to VAR0, VAR1, ...
- ✅ Normalizes types to TYPE, numbers to NUM
- ✅ Preserves keywords and operators

### Language-Specific Normalization

**AST-based (Python) or Regex-based (C++/Java)**

```python
# Python: AST-based normalization
normalizer = get_normalizer('python', method='ast')

# C++/Java: Regex-based normalization
normalizer = get_normalizer('cpp', method='regex')
```

**Performance Comparison:**

| Method              | Speed     | Languages         | Best For             |
| ------------------- | --------- | ----------------- | -------------------- |
| **Token** (default) | ⚡ Fast   | Universal         | Production use       |
| AST                 | 🐌 Slower | Python only       | Deep Python analysis |
| Regex               | ⚡ Fast   | Language-specific | C++/Java specific    |

**Recommendation:** Use token-based (default) for production - it's faster and works universally.

### Notebooks

Start with the interactive notebooks to explore each pipeline stage:

```bash
jupyter lab notebooks/
```

**Recommended order:**

1. `00_data_loading.ipynb` - Load and validate data
2. `01_normalization.ipynb` - See before/after normalization
3. `03_ast_similarity.ipynb` - **Compare AST vs RK-GST approaches**
4. `99_end_to_end_demo.ipynb` - Full pipeline demonstration

## ⚙️ Configuration

Edit `src/config/settings.py` to customize:

- Similarity thresholds
- Student-safe bias adjustments
- Supported languages
- Output formats

Edit `src/config/weights.py` to fine-tune:

- Structural similarity method (AST, RK-GST, or HYBRID)
- Feature weights for each signal
- Semantic model selection

## 🔬 Structural Similarity: AST vs RK-GST

The system supports **two structural similarity approaches**:

### AST-based Analysis

- **Best for**: Detecting algorithmic plagiarism
- **Strength**: Semantic understanding, robust to refactoring
- **Use when**: Code has been heavily modified

### RK-GST (Rabin-Karp Greedy String Tiling)

- **Best for**: Copy-paste detection with reordering
- **Strength**: Fast, industry-proven (MOSS, JPlag)
- **Use when**: You need fast screening

### Hybrid Mode (Recommended)

Combines both approaches for robust detection. See `notebooks/03_ast_similarity.ipynb` for side-by-side comparison.

## 📋 Input Format

### CSV Format

```csv
submission_id,code,language
s001,"def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",python
s002,"def fib(x):\n    if x <= 1:\n        return x\n    return fib(x-1) + fib(x-2)",python
```

### JSON Format

```json
{
  "submissions": [
    {
      "submission_id": "s001",
      "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
      "language": "python"
    }
  ]
}
```

## 📊 Output Format

```json
{
  "submission_id": "s002",
  "similarity_score": 95.3,
  "breakdown": {
    "lexical": 88.5,
    "structural": 97.8,
    "semantic": 96.2
  },
  "interpretation": "High structural and semantic similarity detected...",
  "severity": "severe",
  "penalty_decision": "Severe plagiarism",
  "most_similar_to": "s001",
  "confidence": 0.92
}
```

## 🧪 Testing

Run the end-to-end demo notebook to validate the system:

```bash
jupyter notebook notebooks/99_end_to_end_demo.ipynb
```

## 📚 Technical Details

### Normalization Process

1. Remove comments and formatting
2. Normalize variable/function names deterministically
3. Canonicalize control structures (for/while equivalence)
4. Preserve semantic meaning

### Student-Safe Bias

The system applies multiple safeguards:

- Reduce score if only lexical similarity is high
- Boost confidence when structural + semantic agree
- Apply penalty when signals are uncertain
- Never punish standard algorithms alone

### Adaptive Explanations

- **Medium depth** (default): Component breakdown
- **Deep explanation** (auto-activated at ≥70%): Control-flow analysis, algorithm patterns

## 🤝 Contributing

This is a prototype system for academic research. Contributions welcome for:

- Additional language normalizers
- Improved semantic models
- Enhanced student-safe bias logic

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Important Notes

- All submissions must be in the **same programming language**
- Cross-language plagiarism is **not supported**
- Results are offline analysis only (no deployment)
- System is designed for **academic fairness** - independent correct solutions will NOT be flagged

## 📞 Support

For questions or issues, please refer to the notebook documentation and inline code comments.

---

**Built with fairness, transparency, and academic integrity in mind.**

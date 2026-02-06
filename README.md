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
2. **Structural Similarity** (45% weight) - Tree-sitter AST + RK-GST analysis
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
# Clone or navigate to project directory
cd w:/ML_Plagarism

# Install dependencies (includes tree-sitter)
pip install -r requirements.txt
```

**Dependencies include**:

- `tree-sitter>=0.20.0` - Multi-language AST parsing (NEW)
- `tree-sitter-languages>=1.7.0` - Language grammars
- `scikit-learn` - TF-IDF and machine learning
- `transformers` (optional) - CodeBERT for semantic similarity
- Standard libraries: `numpy`, `pandas`, `tqdm`

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

## 🔬 Structural Similarity: Multi-Method Approach

The system supports **three structural similarity methods**:

### Tree-Sitter AST (Default ⭐ Recommended)

- **Best for**: Multi-language plagiarism detection
- **Strength**: Robust error handling, works for Python/Java/C++/C
- **Use when**: You have submissions in multiple languages or student code with errors

### Python AST Analysis

- **Best for**: Deep Python-specific analysis
- **Strength**: Control-flow and data-flow analysis
- **Use when**: All submissions are in Python and you need deep inspection

### RK-GST (Rabin-Karp Greedy String Tiling)

- **Best for**: Copy-paste detection with reordering
- **Strength**: Fast, industry-proven (MOSS, JPlag)
- **Use when**: You need quick screening of many submissions

### Hybrid Mode

Combines all three approaches: Tree-Sitter (40%) + AST (30%) + RK-GST (30%) for maximum accuracy.

See `examples/compare_structural_methods.py` for side-by-side comparison.

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

## 🧪 Testing the Code

### Quick Start Testing

Test the system without Jupyter notebooks using Python scripts:

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Test Individual Components

**A. Test Token Normalization**

```bash
python examples/token_normalizer_demo.py
```

Expected output:

```
======================================================================
TOKEN-BASED NORMALIZATION DEMO
======================================================================

Code 1 - Normalized:
def VAR0 ( VAR1 ) : if VAR1 <= NUM : return NUM return VAR1 * VAR0 ( VAR1 - NUM )

Code 2 - Normalized:
def VAR0 ( VAR1 ) : if VAR1 <= NUM : return NUM return VAR1 * VAR0 ( VAR1 - NUM )

======================================================================
✅ IDENTICAL after normalization!
```

**B. Test Structural Similarity Methods**

```bash
python examples/compare_structural_methods.py
```

Expected output:

```
======================================================================
STRUCTURAL SIMILARITY METHOD COMPARISON
======================================================================

1️⃣  TREE-SITTER (Multi-Language, Robust) ⭐ RECOMMENDED
   Score: 85.7%
   ✅ Multi-language support (Python, Java, C++, C)
   ✅ Robust error handling
   ✅ Fast C-based parser

2️⃣  PYTHON AST (Python-Specific, Deep Analysis)
   Score: 92.3%
   ⚠️  Python only
   ✅ Deep control-flow analysis

3️⃣  RK-GST (Fast String Tiling)
   Score: 78.1%
   ✅ Very fast
   ✅ Good for copy-paste detection
```

**C. Test Normalizer Comparison**

```bash
python examples/compare_normalizers.py
```

#### 3. Test Full Pipeline Programmatically

Create a test script `test_pipeline.py`:

```python
from src.fusion import PlagiarismScorer

# Sample codes
code1 = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""

code2 = """
def compute_fact(number):
    # Calculate factorial
    if number <= 1:
        return 1
    return number * compute_fact(number - 1)
"""

# Initialize scorer
scorer = PlagiarismScorer()

# Analyze similarity
result = scorer.compute_similarity(
    code1, code2,
    language='python',
    normalize=True
)

# Display results
print(f"\n{'='*70}")
print("PLAGIARISM DETECTION RESULTS")
print(f"{'='*70}")
print(f"\nFinal Score: {result['final_score']:.1f}%")
print(f"Severity: {result['severity'].upper()}")
print(f"\nBreakdown:")
for signal, score in result['breakdown'].items():
    print(f"  {signal.capitalize():12} {score:.1f}%")
print(f"\nStructural Method: {result['structural_method']}")
if result['adjustments']:
    print(f"\nAdjustments:")
    for adj in result['adjustments']:
        print(f"  • {adj}")
print(f"{'='*70}\n")
```

Run it:

```bash
python test_pipeline.py
```

Expected output:

```
======================================================================
PLAGIARISM DETECTION RESULTS
======================================================================

Final Score: 94.3%
Severity: SEVERE

Breakdown:
  Lexical      87.2%
  Structural   96.5%
  Semantic     95.8%

Structural Method: treesitter

Adjustments:
  • Boosted by 5.0% (multi-signal agreement)
======================================================================
```

#### 4. Test with Real Data

Create a CSV file `test_submissions.csv`:

```csv
submission_id,code,language
s001,"def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",python
s002,"def fib(x):\n    if x <= 1:\n        return x\n    return fib(x-1) + fib(x-2)",python
s003,"def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",python
```

Test script `test_batch.py`:

```python
from src.io import load_submissions
from src.fusion import PlagiarismScorer

# Load submissions
submissions = load_submissions('test_submissions.csv')

print(f"Loaded {len(submissions)} submissions\n")

# Initialize scorer
scorer = PlagiarismScorer()

# Analyze all
results = scorer.analyze_all(submissions, normalize=True)

# Display results
print("\n" + "="*70)
print("BATCH ANALYSIS RESULTS")
print("="*70)

for res in results:
    severity_emoji = {
        'severe': '🚨',
        'partial': '⚠️ ',
        'clean': '✅'
    }

    print(f"\n{severity_emoji[res['severity']]} {res['submission_id']}")
    print(f"   Similarity: {res['similarity_score']:.1f}%")
    print(f"   Most similar to: {res['most_similar_to']}")
    print(f"   Verdict: {res['severity'].upper()}")

print("\n" + "="*70 + "\n")
```

Run it:

```bash
python test_batch.py
```

### Testing Multi-Language Support

Test with Java code:

```python
from src.fusion import PlagiarismScorer

java_code1 = """
public class Factorial {
    public static int compute(int n) {
        if (n <= 1) return 1;
        return n * compute(n - 1);
    }
}
"""

java_code2 = """
public class Calculator {
    public static int factorial(int num) {
        if (num <= 1) return 1;
        return num * factorial(num - 1);
    }
}
"""

scorer = PlagiarismScorer()
result = scorer.compute_similarity(
    java_code1, java_code2,
    language='java',  # Specify language
    normalize=True
)

print(f"Java Code Similarity: {result['final_score']:.1f}%")
```

### Troubleshooting

**Issue: Tree-sitter import error**

```bash
ModuleNotFoundError: No module named 'tree_sitter'
```

Solution:

```bash
pip install tree-sitter tree-sitter-languages
```

**Issue: Transformers not found (semantic similarity)**

This is optional. The system will fall back to lexical similarity. To enable:

```bash
pip install transformers torch
```

**Issue: AST parsing fails**

The system will gracefully handle this:

- Tree-sitter handles syntax errors automatically
- Python AST will return 0% if code doesn't parse
- RK-GST works on any text

### Performance Testing

Test with larger datasets:

```python
import time
from src.fusion import PlagiarismScorer

# Generate 50 test submissions
submissions = [
    {
        'submission_id': f's{i:03d}',
        'code': f'def func{i}(x): return x * {i}',
        'language': 'python'
    }
    for i in range(50)
]

scorer = PlagiarismScorer()

start = time.time()
results = scorer.analyze_all(submissions)
end = time.time()

print(f"Analyzed {len(submissions)} submissions in {end-start:.2f} seconds")
print(f"Average: {(end-start)/len(submissions)*1000:.2f}ms per submission")
```

### Integration Testing

Test the complete workflow:

```bash
# 1. Test normalization
python examples/token_normalizer_demo.py

# 2. Test structural methods
python examples/compare_structural_methods.py

# 3. Test full pipeline
python test_pipeline.py

# 4. Test batch processing
python test_batch.py
```

All tests should complete without errors. Tree-sitter should show scores for all languages.

## 🎓 For Instructors

### Recommended Testing Workflow

1. **Initial Setup** (5 minutes)

   ```bash
   pip install -r requirements.txt
   python examples/compare_structural_methods.py
   ```

2. **Test with Sample Data** (10 minutes)
   - Create CSV with 3-5 student submissions
   - Run batch analysis
   - Review results

3. **Production Use**
   - Use tree-sitter method (default)
   - Process submissions in batches of 50-100
   - Export results to JSON/CSV for review

## ⚠️ Important Notes

- All submissions must be in the **same programming language**
- Cross-language plagiarism is **not supported**
- Results are offline analysis only (no deployment)
- System is designed for **academic fairness** - independent correct solutions will NOT be flagged

## 📞 Support

For questions or issues, please refer to the notebook documentation and inline code comments.

---

**Built with fairness, transparency, and academic integrity in mind.**

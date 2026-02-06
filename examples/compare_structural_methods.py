"""
Quick comparison: Tree-Sitter vs AST vs RK-GST
Demonstrates the three structural similarity methods.
"""

from src.similarity import (
    TreeSitterStructuralAnalyzer,
    ASTSimilarityAnalyzer,
    RKGSTSimilarityAnalyzer
)

# Sample code (same algorithm, different names)
code1 = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

code2 = """
def compute_fib(number):
    # Base case
    if number <= 1:
        return number
    # Recursive case
    return compute_fib(number - 1) + compute_fib(number - 2)
"""

print("=" * 70)
print("STRUCTURAL SIMILARITY METHOD COMPARISON")
print("=" * 70)

# 1. Tree-Sitter (NEW - multi-language, robust)
print("\n1️⃣  TREE-SITTER (Multi-Language, Robust) ⭐ RECOMMENDED")
ts_analyzer = TreeSitterStructuralAnalyzer()
ts_score = ts_analyzer.compute_similarity(code1, code2, language='python')
print(f"   Score: {ts_score:.1f}%")
print(f"   ✅ Multi-language support (Python, Java, C++, C)")
print(f"   ✅ Robust error handling")
print(f"   ✅ Fast C-based parser")

# 2. Python AST (Python-only, deep analysis)
print("\n2️⃣  PYTHON AST (Python-Specific, Deep Analysis)")
ast_analyzer = ASTSimilarityAnalyzer()
try:
    ast_score = ast_analyzer.compute_similarity(code1, code2)
    print(f"   Score: {ast_score:.1f}%")
    print(f"   ⚠️  Python only")
    print(f"   ✅ Deep control-flow analysis")
except:
    print(f"   ❌ Failed to parse")

# 3. RK-GST (Fast string tiling)
print("\n3️⃣  RK-GST (Fast String Tiling)")
rkgst_analyzer = RKGSTSimilarityAnalyzer()
rkgst_score = rkgst_analyzer.compute_similarity(code1, code2)
print(f"   Score: {rkgst_score:.1f}%")
print(f"   ✅ Very fast")
print(f"   ✅ Good for copy-paste detection")

print("\n" + "=" * 70)
print("VERDICT:")
print("  Tree-Sitter is the BEST choice for production use!")
print("  - Works for multiple languages")
print("  - Handles errors gracefully  ")
print("  - Industry-proven (GitHub, Atom)")
print("=" * 70)

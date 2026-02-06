"""
Quick comparison: Token vs AST normalization
"""

# Example code
code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""

print("=" * 70)
print("NORMALIZATION METHOD COMPARISON")
print("=" * 70)

# Token-based (universal, fast)
from src.normalization.token_normalizer import TokenNormalizer
token_norm = TokenNormalizer()
token_result = token_norm.normalize(code)

print("\n1️⃣  TOKEN-BASED (Universal):")
print(f"   Output: {token_result[:80]}...")
print(f"   Length: {len(token_result.split())} tokens")
print(f"   Speed: ⚡ FAST")
print(f"   Languages: Python, C++, Java, etc.")

# AST-based (Python only)
from src.normalization.python_normalizer import PythonNormalizer
ast_norm = PythonNormalizer()
ast_result = ast_norm.normalize(code)

print("\n2️⃣  AST-BASED (Python-specific):")
print(f"   Output: {ast_result[:80]}...")
print(f"   Length: {len(ast_result)} characters")
print(f"   Speed: 🐌 Slower")
print(f"   Languages: Python only")

print("\n" + "=" * 70)
print("RECOMMENDATION: Use TOKEN-BASED for production (faster, universal)")
print("=" * 70)

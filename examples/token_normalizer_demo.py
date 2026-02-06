"""
Example: Using the new token-based normalizer
"""

from src.normalization import get_normalizer

# Sample codes (same algorithm, different names)
code1 = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""

code2 = """
def compute_fact(number):
    # Base case
    if number <= 1:
        return 1
    # Recursive step
    return number * compute_fact(number - 1)
"""

print("=" * 70)
print("TOKEN-BASED NORMALIZATION DEMO")
print("=" * 70)

# Get token normalizer (default)
normalizer = get_normalizer('python')  # method='token' by default

# Normalize both codes
norm1 = normalizer.normalize(code1)
print("\nCode 1 - Normalized:")
print(norm1)

normalizer.reset_counters()
norm2 = normalizer.normalize(code2)
print("\nCode 2 - Normalized:")
print(norm2)

# Check if they're similar
print("\n" + "=" * 70)
if norm1 == norm2:
    print("✅ IDENTICAL after normalization!")
    print("   The normalizer successfully removed cosmetic differences.")
else:
    # Calculate similarity
    tokens1 = set(norm1.split())
    tokens2 = set(norm2.split())
    similarity = len(tokens1 & tokens2) / len(tokens1 | tokens2) * 100
    print(f"📊 {similarity:.1f}% similar after normalization")
    print(f"   Common tokens: {len(tokens1 & tokens2)}/{len(tokens1 | tokens2)}")

print("=" * 70)

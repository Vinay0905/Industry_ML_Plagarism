"""
Test the complete plagiarism detection pipeline.
Run this to verify the system works end-to-end.
"""

from src.fusion import PlagiarismScorer

# Sample codes (same algorithm, renamed)
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

print("=" * 70)
print("PLAGIARISM DETECTION PIPELINE TEST")
print("=" * 70)

# Initialize scorer
scorer = PlagiarismScorer()

# Analyze similarity
print("\nAnalyzing similarity...\n")
result = scorer.compute_similarity(
    code1, code2, 
    language='python', 
    normalize=True
)

# Display results
print("=" * 70)
print("RESULTS")
print("=" * 70)
print(f"\nFinal Score: {result['final_score']:.1f}%")
print(f"Severity: {result['severity'].upper()}")

print(f"\nBreakdown:")
for signal, score in result['breakdown'].items():
    print(f"  {signal.capitalize():12} {score:.1f}%")

print(f"\nStructural Method: {result['structural_method']}")

if result['structural_breakdown']:
    print(f"\nStructural Breakdown:")
    for method, score in result['structural_breakdown'].items():
        print(f"  {method.upper():12} {score:.1f}%")

if result['adjustments']:
    print(f"\nStudent-Safe Adjustments:")
    for adj in result['adjustments']:
        print(f"  • {adj}")

print("\n" + "=" * 70)

# Interpretation
if result['severity'] == 'severe':
    print("🚨 SEVERE PLAGIARISM DETECTED")
    print("   Recommendation: Investigate immediately")
elif result['severity'] == 'partial':
    print("⚠️  PARTIAL SIMILARITY DETECTED")
    print("   Recommendation: Review manually")
else:
    print("✅ CODE APPEARS CLEAN")
    print("   Recommendation: No action needed")

print("=" * 70 + "\n")

"""
Batch testing with multiple submissions.
Demonstrates analyzing multiple code submissions at once.
"""

from src.io import load_submissions
from src.fusion import PlagiarismScorer
import pandas as pd

# Create sample data
print("Creating sample submissions...")
sample_data = {
    'submission_id': ['s001', 's002', 's003', 's004'],
    'code': [
        # s001 - Fibonacci recursive
        """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""",
        # s002 - Same as s001 but renamed
        """
def fib(x):
    if x <= 1:
        return x
    return fib(x-1) + fib(x-2)
""",
        # s003 - Factorial (different algorithm)
        """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
""",
        # s004 - Fibonacci iterative (different approach)
        """
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
"""
    ],
    'language': ['python', 'python', 'python', 'python']
}

# Save to CSV
df = pd.DataFrame(sample_data)
df.to_csv('test_submissions.csv', index=False)
print(f"✓ Created test_submissions.csv with {len(df)} submissions\n")

# Load submissions
submissions = load_submissions('test_submissions.csv')
print(f"Loaded {len(submissions)} submissions\n")

# Initialize scorer
scorer = PlagiarismScorer()

# Analyze all
print("Analyzing pairwise similarities...\n")
results = scorer.analyze_all(submissions, normalize=True)

# Display results
print("=" * 70)
print("BATCH ANALYSIS RESULTS")
print("=" * 70)

severity_emoji = {
    'severe': '🚨',
    'partial': '⚠️ ',
    'clean': '✅'
}

for res in sorted(results, key=lambda x: x['similarity_score'], reverse=True):
    print(f"\n{severity_emoji[res['severity']]} {res['submission_id']}")
    print(f"   Similarity: {res['similarity_score']:.1f}%")
    print(f"   Most similar to: {res['most_similar_to']}")
    print(f"   Verdict: {res['severity'].upper()}")
    print(f"   Breakdown:")
    for signal, score in res['breakdown'].items():
        print(f"     {signal.capitalize():10} {score:.1f}%")

print("\n" + "=" * 70)

# Summary statistics
severe_count = sum(1 for r in results if r['severity'] == 'severe')
partial_count = sum(1 for r in results if r['severity'] == 'partial')
clean_count = sum(1 for r in results if r['severity'] == 'clean')

print("\nSUMMARY STATISTICS")
print("=" * 70)
print(f"Total submissions: {len(results)}")
print(f"  🚨 Severe:  {severe_count} ({severe_count/len(results)*100:.1f}%)")
print(f"  ⚠️  Partial: {partial_count} ({partial_count/len(results)*100:.1f}%)")
print(f"  ✅ Clean:   {clean_count} ({clean_count/len(results)*100:.1f}%)")
print("=" * 70 + "\n")

print("✓ Test completed successfully!")
print("  CSV file: test_submissions.csv")
print("  You can now modify the CSV and re-run this script.\n")

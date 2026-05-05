#!/usr/bin/env python3
"""
Run from the backend/ directory:
    python scripts/eval.py

Reads all 30 precomputed pair files and prints a distribution report.
Useful for verifying that scoring changes shift outcomes the expected way.
"""
import json
from collections import Counter
from pathlib import Path

PRECOMPUTED_DIR = Path(__file__).parent.parent / "app" / "data" / "precomputed"

files = sorted(
    p for p in PRECOMPUTED_DIR.glob("*.json")
    if p.parent == PRECOMPUTED_DIR  # exclude v1/ subdir
)

if not files:
    print("No precomputed files found. Run precompute_responses.py first.")
    raise SystemExit(1)

venue_counts: Counter = Counter()
compat_counts: Counter = Counter()
venue_scores: list[int] = []
compat_scores: list[int] = []

for f in files:
    data = json.loads(f.read_text())
    venue_counts[data["venue"]["venue"]["name"]] += 1
    venue_scores.append(data["venue"]["score"])
    compat_counts[data["compatibility"]["label"]] += 1
    compat_scores.append(data["compatibility"]["score"])

total = len(files)
BAR_WIDTH = 24


def bar(count: int, total: int) -> str:
    filled = round(count / total * BAR_WIDTH)
    return "█" * filled


print(f"\nDate Architect — Scoring Evaluation ({total} pairs)\n")

print("Venue distribution:")
for name, count in venue_counts.most_common():
    pct = count / total * 100
    print(f"  {name:<28} {count:>2}/{total}  ({pct:>3.0f}%)  {bar(count, total)}")

print()

label_order = ["Highly Compatible", "Complementary", "Interesting Mix", "High Contrast"]
print("Compatibility distribution:")
for label in label_order:
    count = compat_counts.get(label, 0)
    pct = count / total * 100
    print(f"  {label:<24} {count:>2}/{total}  ({pct:>3.0f}%)")

print()
print(f"Avg venue score:  {sum(venue_scores) / total:.1f} / 100")
print(f"Score range:      {min(venue_scores)} – {max(venue_scores)}")
print()
print(f"Avg compatibility score:  {sum(compat_scores) / total:.1f} / 100")
print(f"Compatibility range:      {min(compat_scores)} – {max(compat_scores)}")
print()

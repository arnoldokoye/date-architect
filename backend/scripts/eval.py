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

# --- Outcome data (only shown if outcomes.db exists) ---
import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent.parent))

_db_path = Path(__file__).parent.parent / "app" / "data" / "outcomes.db"

if _db_path.exists():
    from app.db import get_outcome_stats
    stats = get_outcome_stats()
    n = stats["total_outcomes"]

    print(f"Outcome data ({n} recorded):")
    if n == 0:
        print("  No outcomes recorded yet. Run scripts/seed_outcomes.py first.")
    else:
        for vid, counts in sorted(stats["by_venue"].items()):
            gd = counts.get("great_date", 0)
            wt = counts.get("went", 0)
            sk = counts.get("skipped", 0)
            print(f"  {vid:<28}  great_date: {gd}   went: {wt}   skipped: {sk}")

        print()
        print("Algorithm pick rate vs great_date rate:")
        for name, algo_count in venue_counts.most_common():
            vid = next(
                (json.loads(f.read_text())["venue"]["venue"]["id"]
                 for f in files
                 if json.loads(f.read_text())["venue"]["venue"]["name"] == name),
                None,
            )
            if vid is None or vid not in stats["by_venue"]:
                continue
            vcounts = stats["by_venue"][vid]
            venue_total = sum(vcounts.values())
            if venue_total == 0:
                continue
            algo_pct = algo_count / total * 100
            gd_pct = vcounts.get("great_date", 0) / venue_total * 100
            gap = gd_pct - algo_pct
            indicator = "↑ under-recommended" if gap > 15 else ("↓ over-recommended" if gap < -15 else "~")
            print(f"  {name:<28}  picks: {algo_pct:>3.0f}%   great_date rate: {gd_pct:>3.0f}%   {indicator}")
    print()

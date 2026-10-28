"""Recompute canonical result files and their paper copies without changing datasets.

Both analyses must succeed before any published result file is replaced. Historical
outputs stay under prototype/legacy rather than being presented as current runs.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT.parent/'midterm/review'
JOBS = [
    ('backtest.py', 'uiuc_data_scaled.json', 'backtest_results_scaled.json', 'scaled-backtest.json', 'scaled-run.json'),
    ('citation_impact.py', 'uiuc_data_scaled.json', 'citation_impact.json', 'citation-impact.json', 'citation-run.json'),
]


def main():
    with tempfile.TemporaryDirectory(prefix='bridgefinder-results-') as scratch:
        scratch = Path(scratch)
        for script, dataset, result, _, manifest in JOBS:
            subprocess.run([sys.executable, str(ROOT/script), '--data', str(ROOT/dataset),
                            '--out', str(scratch/result), '--manifest-out', str(scratch/manifest)], check=True)
        (ROOT/'results').mkdir(exist_ok=True)
        REVIEW.mkdir(exist_ok=True)
        for _, _, result, paper_copy, manifest in JOBS:
            shutil.copyfile(scratch/result, ROOT/'results'/result)
            shutil.copyfile(scratch/result, REVIEW/paper_copy)
            shutil.copyfile(scratch/manifest, ROOT/'results'/manifest)
            shutil.copyfile(scratch/manifest, REVIEW/manifest)
    print('Canonical results, paper copies, and provenance sidecars refreshed. No datasets were modified.')


if __name__ == '__main__':
    main()

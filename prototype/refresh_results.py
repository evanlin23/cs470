"""Recompute the canonical result files and their provenance sidecars without changing datasets.

Every analysis must succeed before any published result file is replaced.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
DATASET = ROOT/'uiuc_data_scaled.json'
JOBS = [
    ('backtest.py', 'backtest_results_scaled.json', 'scaled-run.json'),
    ('citation_impact.py', 'citation_impact.json', 'citation-run.json'),
    ('network_stats.py', 'network_stats.json', 'network-run.json'),
]


def main():
    with tempfile.TemporaryDirectory(prefix='bridgefinder-results-') as scratch:
        scratch = Path(scratch)
        for script, result, manifest in JOBS:
            subprocess.run([sys.executable, str(ROOT/script), '--data', str(DATASET),
                            '--out', str(scratch/result), '--manifest-out', str(scratch/manifest)], check=True)
        (ROOT/'results').mkdir(exist_ok=True)
        for _, result, manifest in JOBS:
            shutil.copyfile(scratch/result, ROOT/'results'/result)
            shutil.copyfile(scratch/manifest, ROOT/'results'/manifest)
    print('Canonical results and provenance sidecars refreshed. No datasets were modified.')


if __name__ == '__main__':
    main()

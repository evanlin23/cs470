#!/bin/bash
set -e

echo "=== BridgeFinder Experiment Runner ==="

# 1. Install prerequisites
echo "[Step 1/3] Checking dependencies..."
python3 -m pip install -q --user --break-system-packages networkx scipy 2>/dev/null || true

# 2. Fetch data from OpenAlex API
echo "[Step 2/3] Harvesting UIUC co-authorship records from OpenAlex API..."
# Set your NetID / email to join the polite pool (10x faster)
MAILTO="${1:-elin26@illinois.edu}"
python3 prototype/fetch_openalex.py --mailto "$MAILTO" --max_works 5000 --out prototype/uiuc_data.json

# 3. Run temporal backtest & evaluation across baselines
echo "[Step 3/3] Running temporal backtest across 4 baselines..."
python3 prototype/backtest.py --data prototype/uiuc_data.json --out prototype/results/backtest_results.json

echo "=== Experiment Complete! Results saved to prototype/results/backtest_results.json ==="

# BridgeFinder final report

`latex/main.tex` is the CS 470 final report in ACM format (`acmart`, `sigconf`). It is due Wednesday, December 9, 2026, at 5:00 pm. It should run 10 to 12 pages plus references.

## Build

From `final/latex`:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The folder is self-contained (`main.tex`, `references.bib`, `figures/`), so you can also zip it and upload it to Overleaf with the pdfLaTeX compiler.

## Before submitting

1. Fill in every red **PENDING** marker. Run `grep -n pending latex/main.tex` to list them. Almost all of them wait on the student study.
   - Collect the pasted answers and run `python prototype/study/import_answers.py replies/*.txt --out /private/folder`.
   - For the one-minute study, run `python prototype/study/analyze_quick.py --responses /private/folder/quick_sessions.json --card-features prototype/study/card_features.json --out /private/folder/quick-analysis.json`.
   - For moderated or full sessions, run `python prototype/study/analyze_study.py --responses /private/folder/sessions.json --card-features prototype/study/card_features.json --out /private/folder/study-analysis.json`.
   - Never commit participant answers.
2. Check the AI Use and Contributions sections. They are your own statements.
3. Run the tests from the repository root:
   ```bash
   python -m unittest discover -s prototype/tests -v
   ```
   `test_final_consistency.py` fails if any number in the paper's tables, figures or quoted comparisons drifts from `prototype/results/final_analysis.json` or `final_example.json`.

## Where the numbers come from

| Paper section | Result file | Script |
|---|---|---|
| Training-graph table, Sections 3.4 and 3.5 | `results/network_stats.json`, `results/backtest_results_scaled.json` | `network_stats.py`, `backtest.py` |
| Community table, Section 3.2 | `results/final_analysis.json` → `communities` | `final_analysis.py --part communities` |
| Historical results table, Section 6.1 | `results/final_analysis.json` → `ranking` | `final_analysis.py --part ranking` |
| Validation figure, Section 6.2 | `results/final_analysis.json` → `validation` | `final_analysis.py --part validate` |
| Worked-example table, Section 6.1 | `results/final_example.json` | `final_example.py` |

Every result file has a manifest with hashes of the dataset and the code that produced it. `final_analysis.py` never changes the deployed model, app or study cards. Running all its parts takes about 20 minutes on four cores.

## Style

The style rules carry over from the midterm (`midterm/review/rewrite-guide.md`):
- plain "we"-led prose, with no colons, semicolons or em dashes in authored text
- P@10 is the headline historical metric
- never invent participant details
- keep "approved of the app" for round 2

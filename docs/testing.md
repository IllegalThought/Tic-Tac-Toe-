# Validation

Run commands from the project root. Use the `.venv` interpreter shown in README.

```bash
python -m unittest discover -s tests -v
python tools/benchmark.py
```

## Recorded results

- 10 rule/search tests passed on Python 3.12 in 43.897 seconds.
- 3 real GUI lifecycle tests passed on a virtual X display in 1.707 seconds after final layout and shutdown adjustments.
- Offline dependency installation passed in a fresh virtual environment with `--no-index --find-links vendor`.
- Application window rendered at 1180×860 and was visually inspected. `gui_preview.png` records a real human-center/AI-response position. Font and corner rendering can differ by OS.
- Source compilation passed.

Timing is environment-specific. Tests have been run on Linux; Windows and macOS have documented commands but were not directly tested here.

## Test coverage

Rules: empty immutable board, legal/occupied/out-of-range moves, every win line for both sides, draw, terminal action prevention, turn management, score reset and restart.

Search: immediate win, necessary block, terminal no-move result; baseline/alpha-beta/optimized agreement on sampled positions; optimized scores and each root candidate checked against an independent reference solver on every reachable nonterminal position for either starter; all human reply sequences against each exact engine's chosen O policy, with either starter; eight symmetries; symmetry-disabled table; cold cache repeatability; exact/lower/upper entry types; known two-node counter fixture; experimental depths; iterative/direct horizon equivalence; bounded heuristics.

GUI: board button invokes a move; input rejected while busy or after game completion; worker response appears; analysis and comparison update; tree/info windows open; score reset; restart; starter selection; all modes selectable; depth controls and iterative horizon applied; stale generation results ignored; clean closure.

GUI tests skip when a desktop display or GUI dependencies are unavailable. Core tests remain executable headlessly. A skipped GUI test is not proof of GUI validation on that machine.

## Manual presentation checklist

1. Play a complete game using each full-depth mode; confirm terminal announcement and winning-cell highlight where applicable.
2. Switch starter and inspect default AI response.
3. Compare the latest pre-decision snapshot; inspect equal game values and measured counters.
4. Inspect the recorded tree and explain bounds versus exact alternative scores.
5. Try shallow experimental mode and explain why it may fail.
6. Restart during baseline computation, confirm new board is unaffected by the old result.
7. Close the window while computation runs; app should exit.

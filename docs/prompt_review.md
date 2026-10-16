# Prompt analysis and implementation decisions

The supplied prompt is internally consistent and specifies classical game search rather than machine learning. Its highest-risk requirements are alpha-beta bound caching, symmetry coordinate handling, fair measurements and responsive GUI integration.

| Requirement | Delivered decision |
| --- | --- |
| Four algorithm modes | Baseline Minimax; basic alpha-beta; full optimized search; experimental depth-limited alpha-beta |
| Exact optimal behavior | Full-depth search with independently verified values and never-lose policy checks |
| Caching and symmetry | Side/horizon-aware score keys; EXACT/LOWER/UPPER entries; eight transformations; cold per-decision table |
| Alternative move scores | Full-window search for each candidate to avoid presenting bounds as exact scores |
| Metric honesty | Calls, evaluated terminal leaves, cutoff events and immediate skipped children measured separately |
| Responsive desktop game | Worker queue and main-thread Tk callbacks; stale-result generation guard |
| Depth and iterative deepening | Configurable 1–9 horizon and cumulative iterative search; explicitly experimental |
| Search visualization | Optional bounded real text tree at levels 1–2, not a full graphical tree |
| GUI design | Dark cards, colored X/O, hover feedback, winning highlights, scrollable analysis and comparison bars |
| Academic documentation | Architecture, scoring, flowcharts, actual measurements, report, test evidence and viva answers |
| Clean source organization | Shared recursion instead of duplicating Minimax/alpha-beta across separate files |

Terminal scores use ±(100−occupied cells), rather than ±10, to keep heuristic estimates below all wins and provide root-independent memoization. The application intentionally uses modest turn/hover feedback instead of elaborate animation. Comparisons are honest all-candidate searches, not claimed best-move-only benchmarks. Python and platform Tk remain prerequisites; the ZIP is not a native executable.

# Intelligent Tic-Tac-Toe Game Agent Using Minimax, Alpha-Beta Pruning and Optimized Search

## Introduction and problem statement

Tic-Tac-Toe is a small deterministic game that permits complete adversarial search and exhaustive correctness validation. The problem is to choose a legal action maximizing the agent's outcome against an optimal opponent, while measuring how traversal strategies change computational effort. A visually usable game makes state transitions and search behavior accessible during a live demonstration.

## Objectives

Implement playable human-versus-agent gameplay; demonstrate rational action selection; compare baseline Minimax, alpha-beta and optimized search; expose measured statistics; and distinguish exact decisions from heuristic estimates. Correctness takes priority over speed.

## Technologies

Python 3.11+, CustomTkinter 5.2.2 and Tk; tuples/dictionaries; `threading`, `queue`, `time.perf_counter`; `unittest`. Dependency wheels are included for offline installation. No ML models or external APIs.

## System and workflow

See `architecture.md`. Launch → human move validation → terminal check → worker search → main-thread result acceptance → O placement → dashboard update → terminal check → next turn. Either player can start; restart invalidates stale results. Winning cells turn green. X is cyan and O is coral. Scores last only for the session.

## Intelligent-agent model and syllabus mapping

| Unit | Demonstrated concepts | Implementation |
| --- | --- | --- |
| I | Agents, environment, rational behavior, percepts/actions | Board snapshot → best legal action; fully observable adversarial game |
| II | State spaces, heuristic functions, depth control, iterative deepening | Immutable search states; bounded evaluation; experimental depth 1–9 |
| III | Optimal game decisions, MAX/MIN, Minimax, alpha-beta | Three exact full-depth modes and measured comparison |
| Additional optimizations | Transpositions and symmetry | Bound-aware local table, eight board transformations |

This project does not implement BFS, A*, reinforcement learning, neural networks, knowledge representation systems or unrelated syllabus topics. Syllabus mapping follows the concepts stated in the supplied project prompt; it is not a claim to cover an entire course.

## Algorithms

See `algorithms.md` for scoring, heuristics, flowcharts, search-tree example, bounds and complexity. Full-depth O maximizes utility. Values are O-relative even when evaluating a position where X moves next. Experimental shallow values are estimates and can yield losses.

## Interface explanation

Left panel: scorecards, turn/result, 3×3 board, new game, reset scores. Header: mode and starter; depth/iterative settings enabled only in experimental mode. Scrollable right panel: eight latest-decision metrics; derived explanation; candidate values; cold-cache comparison table and node bar chart; limited actual search-tree trace; definitions window. Computation occurs on workers while Tk polls a queue.

## Testing and performance analysis

See `testing.md` and `benchmark_results.md`. Benchmark values are generated from code, not constants. Timing depends on hardware, concurrent processes and interpreter overhead. The optimization objective is proven reduced traversal while retaining the same exact value; wall-clock wins are not guaranteed on small positions. Baseline and basic alpha-beta use identical row-major ordering. Optimized mode intentionally also changes ordering and cache policy.

## Results and observations

All three exact modes agree on the sampled comparison positions. Exhaustive optimized checks compare every reachable nonterminal board, for either starter and side, and every candidate score, against an independent memoized reference solver. All exact modes are tested against every human response along their chosen policies with either starter. Full-depth play never loses in those checks. Empty-board optimum is a draw. Tables exploit repeated positions and square symmetry. Shallow search illustrates the tradeoff between horizon and confidence. Recorded measurements are in the adjacent benchmark file.

## Limitations

Small fixed 3×3 board; fixed O agent/X human; session-only scores; fixed-size desktop working area; bounded text search tree; no hard time budgets. Workers are not forcibly cancelled on restart, although stale results are ignored. Exhaustive baseline can be slow. The GUI uses light hover/turn feedback, without elaborate animations. Bundled Python wheels do not include Python itself or the platform's Tk runtime. This educational project is not evidence of scalable performance on chess-sized trees.

## Future scope

Add a time-budgeted iterative solver with safe cancellation; configurable board sizes with appropriate terminal rules; replay/export of search data; best-move-only versus all-candidates measurement mode; and accessibility controls. Larger games need revised evaluation and validation rather than a simple board-size parameter.

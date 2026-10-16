# Viva questions with answers

1. **Why is this AI, rather than ML?** It chooses rational actions using explicit game search. No parameters are learned from examples.
2. **What are percept, action and environment?** Board/turn; placement of O in an empty cell; the game board and opposing player.
3. **Why use Minimax?** Alternating turns have conflicting objectives: O maximizes and X minimizes the same utility.
4. **What does optimal opposition mean?** Each future player chooses their best available outcome. A human mistake can let the AI win even from a theoretically drawn state.
5. **Why does alpha-beta preserve the answer?** It omits branches already bounded so they cannot improve the ancestor's decision.
6. **What are alpha and beta?** Lower bound guaranteed to MAX and upper bound guaranteed to MIN within the current search window.
7. **What is the cutoff condition?** Alpha ≥ beta.
8. **Is a cutoff value exact?** Not necessarily. It can be a lower or upper bound and must be stored as such.
9. **Why order moves?** Promising moves can tighten bounds sooner. Ordering changes efficiency, not exact full-depth value.
10. **What is a transposition?** The same position reached through different move sequences.
11. **Why include side and depth in cache keys?** The player who moves changes the value, and different horizons can produce incompatible estimates.
12. **Why cache scores rather than moves?** Symmetry changes coordinates. A canonical score can be reused without transforming a returned move.
13. **Why eight symmetries?** A square has four rotations and four reflected orientations.
14. **How is terminal scoring cache-safe?** It uses absolute occupied-cell count, not distance from a different root. O win is 100−occupied; X win is its negative.
15. **Can the heuristic override a win?** No: it is clamped to ±50, below all terminal win magnitudes, and terminal checks run first.
16. **Does iterative deepening reduce total work?** Not automatically. It repeats smaller horizons; this implementation accumulates that work and has no time budget.
17. **Can depth-limited AI lose?** Yes. It may miss threats beyond its horizon. Full-depth is separately tested for perfect play.
18. **Why might two correct engines choose different moves?** Several moves can have the same optimal value; ordering determines tie resolution.
19. **Are skipped descendants counted?** No. Only immediate unvisited siblings at cutoff events are measured.
20. **Do cache hits equal distinct states?** No. Nodes are calls, cache hits are successful lookups, and stored keys count table entries.
21. **How is the comparison fair?** Same snapshot, side, terminal utility, full horizon, independent cold tables and full windows at root candidates. Optimized ordering is explicitly disclosed.
22. **Why can optimized be slower despite fewer nodes?** Computing tactical priorities and canonical symmetries has overhead, especially on tiny trees.
23. **How is the GUI responsive?** A worker computes; Tk polls a queue and updates widgets on its main thread.
24. **What if New game is pressed during search?** The generation changes, so the old result is ignored. The worker may finish in the background.
25. **What did you verify exhaustively?** Optimized values and candidates on every reachable nonterminal position, and all human responses against each exact engine's selected policy, with either starter.
26. **Which improvements are extra to the syllabus?** Transposition caching and symmetry, as identified in the supplied prompt.
27. **What is Minimax complexity?** Worst-case O(b^d); favorable alpha-beta ordering can approach O(b^(d/2)), though Tic-Tac-Toe's branching factor decreases each ply.
28. **Why does the empty-board game end in a draw under optimal play?** Neither player can force a win against perfect opposition; the complete game-tree value is zero.

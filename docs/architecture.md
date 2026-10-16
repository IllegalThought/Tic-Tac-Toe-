# Architecture and agent model

UI → GameManager → immutable board snapshot → Engine → Result → main-thread UI.

`main.py` validates Python version and launches CustomTkinter. The manager owns the live board, player turn, terminal flag and session counters. Board functions validate legal placements. AI never changes the live board: every child is a new tuple.

The GUI sends a snapshot and settings to a daemon worker. The worker only calculates and pushes a result or error into a queue. A Tk `after(40, ...)` callback polls that queue. Tk widgets are touched only on the main thread. The board disables input during AI computation. A generation number invalidates old results after restart or closure. Workers already running are not forcibly cancelled, but their stale results cannot change a new game. Repeated restarts during baseline searches can temporarily consume CPU.

Agent: deterministic adversarial-search program. Percept: board and side to move. Action: place O in an empty cell. Performance measure: best achievable result, preferring faster wins and delaying unavoidable losses. Environment: fully observable, deterministic, discrete, sequential, two-player adversarial; static during an individual turn, except that human input determines the next state. This is classical AI, not learned behavior.

Search configuration lives in `ai/search.py`; recursion is shared so terminal scoring and counters stay consistent. GUI imports no search implementation details beyond results and mode selection. Caches are local to a single decision, keyed by board/side/horizon, with no stored coordinates.

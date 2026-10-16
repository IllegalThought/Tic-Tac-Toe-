# Intelligent Tic-Tac-Toe Game Agent

A Python desktop AI mini-project with a CustomTkinter dashboard, four working search modes, honest performance counters, and classical AI documentation. Human = X; agent = O. No accounts, APIs, models, databases or external services are used.

## Quick start

**Extract the ZIP first. Do not run files inside the compressed folder.** Install Python 3.11+ with Tk support. Open a terminal in the extracted `ai_tic_tac_toe` folder (the folder containing `main.py`).

### Windows (Command Prompt or VS Code terminal)

```bat
py -3 -m venv .venv
.venv\Scripts\python -m pip install --no-index --find-links vendor -r requirements.txt
.venv\Scripts\python main.py
```

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --find-links vendor -r requirements.txt
.venv/bin/python main.py
```

Dependency wheels are included under `vendor/`, so installation can work without internet. Python and the OS Tk runtime must already be installed. These are source files, not a standalone `.exe`.

Alternatively activate the environment, run `python -m pip install -r requirements.txt`, then `python main.py`.

## VS Code

1. File → Open Folder → extracted `ai_tic_tac_toe`.
2. Open Terminal → New Terminal, then run the commands above for your OS.
3. Install the Microsoft Python extension if needed.
4. Use Python: Select Interpreter and select `.venv`.
5. Open `main.py` and choose Run Python File in Terminal.

## How to demonstrate the game

- Click an empty cell. Input locks while the agent computes.
- Default mode is Fully Optimized AI. Select the other full-depth modes to compare behavior.
- Choose Human starts or AI starts. Changing the starter begins a new game.
- Experimental mode enables depth 1–9 and optional iterative deepening. It may lose at shallow depth.
- New game resets board and analysis, preserving scores. Reset scores changes counters only.
- Compare algorithms runs three fresh engines on **the latest AI pre-move board**, or the current board before any decision. It does not change the live board.
- View search tree shows a bounded text tree of real visited nodes from the latest decision. It is a trace, not a rendering of the whole game tree.
- Metric definitions & syllabus explains counters and course alignment.

## Automated checks

Windows:

```bat
.venv\Scripts\python -m unittest discover -s tests -v
.venv\Scripts\python tools\benchmark.py
```

macOS / Linux:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/benchmark.py
```

After activation, `python -m unittest discover -s tests -v` works too. Tests do not need a display or CustomTkinter. Exhaustive checks can take around a minute or longer on slower hardware. GUI tests in `tests/test_gui.py` skip automatically without a desktop display.

## Project layout

```text
main.py                 Desktop entry point
requirements.txt        Minimal GUI dependency
vendor/                 Offline dependency wheels and license notes
ai/search.py            Separate mode configurations, Minimax and alpha-beta recursion
ai/heuristics.py        Tactical ordering and bounded cutoff evaluation
ai/symmetry.py          Eight square symmetries and canonical key
 game/board.py          Immutable board, validation and terminal rules
 game/game_manager.py   Turns, outcomes, restart and session scores
 gui/app.py             Dashboard, workers, board, comparison chart and trace window
 tests/                 Rules, exhaustive AI checks, GUI lifecycle checks
 tools/benchmark.py     Reproducible measured comparisons
 docs/                  Architecture, algorithms, report, viva, testing and results
```

The engines share a recursion implementation to avoid duplicated scoring logic. Standard Minimax disables both pruning and caching; basic alpha-beta uses the same row-major ordering as baseline. Optimized mode enables tactical ordering, bound-aware caching and symmetry. Each root candidate receives a full search window, making all displayed alternative scores exact for the selected horizon; this costs extra work compared with a best-move-only root search.

## Troubleshooting

- **`py` not found (Windows):** Install Python 3.11+ and enable Add Python to PATH; try `python` instead of `py -3`.
- **Missing CustomTkinter:** Install dependencies with the same Python interpreter that launches `main.py`.
- **Missing `_tkinter` or `tkinter`:** On Windows use the Python installer with Tcl/Tk enabled. On macOS use a Python distribution that includes Tk (such as the python.org installer). On Debian/Ubuntu install `python3-tk` and `python3-venv`. Test with `python3 -m tkinter` (or `py -3 -m tkinter`). Tk is an OS/Python component; pip cannot fix a missing Tk runtime.
- **No display / `$DISPLAY` error:** Run on a local desktop, not a headless server or notebook. This is a desktop app.
- **PowerShell blocks activation:** The commands above use the environment's interpreter directly, so activation is unnecessary.
- **Missing `main.py`:** Check the current folder. Enter the extracted `ai_tic_tac_toe` directory.
- **Window too large:** A desktop working area of about 1000×820 pixels is recommended. Reduce OS display scaling if needed. The analysis panel scrolls.
- **Minimax takes longer:** Expected, especially when AI starts. Its exhaustive baseline is intentionally unoptimized. The GUI remains scheduled while work runs on a background thread.
- **Different tied moves:** Engines can choose different coordinates with equal optimal values. Compare values, not coordinates.

Read `docs/project_report.md` for your report and `docs/viva_questions.md` before presenting. Do not claim depth-limited search is unbeatable or that this project uses machine learning.

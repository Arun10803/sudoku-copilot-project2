# Project Instructions — Sudoku (Python + Flask)

- Build the application using **Python** and **Flask** with server-rendered HTML (`templates/index.html`), CSS (`static/styles.css`), and JSON API endpoints in `app.py`.
- Generate Sudoku puzzles in `sudoku_engine.py` using backtracking with Minimum Remaining Values (MRV) and verify uniqueness (`count_solutions(..., limit=2) == 1`).
- Detect row, column, and 3x3 box conflicts accurately and persist Top 10 leaderboard scores in `storage.py`.
- Include unit tests in `tests/test_sudoku.py` runnable via `pytest` and store required Copilot milestone screenshots under `Screenshots/`.
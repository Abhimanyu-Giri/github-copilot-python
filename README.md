# Flask Sudoku Game

## Project Overview

This repository contains a Flask-backed Sudoku game. Sudoku generation and unique-solution validation run in Python, while the browser provides the interactive board, timer, hints, completion feedback, theme preference, and local Top 10 leaderboard.

## Features

- Generates valid 9x9 puzzles with exactly one solution.
- Easy, Medium, and Hard difficulty levels.
- Immediate row, column, and 3x3 box conflict feedback.
- Check Puzzle validation against the server-side solution.
- One-cell hints that become locked and visually distinct.
- Elapsed MM:SS timer that stops on correct completion.
- Accessible controls, status messages, keyboard focus indicators, and dark mode.
- Persistent Top 10 leaderboard in browser localStorage.
- Responsive board and controls for desktop and mobile screens.

## Project Structure

```text
starter/
  app.py                 Flask routes and current game state
  sudoku_logic.py        Sudoku generation, validation, and solution counting
  requirements.txt       Flask and pytest dependencies
  static/
    main.js              Browser game behavior and localStorage features
    styles.css           Light/dark themes and responsive layout
  templates/
    index.html            Semantic game and leaderboard markup
  tests/
    test_app.py          Flask route and interface-hook tests
    test_sudoku_logic.py Sudoku generation and solver tests
Screenshots/              Required Copilot and feature evidence
```

## Prerequisites

- Python 3.9 or newer
- A modern browser with JavaScript, localStorage, and CSS support

## Setup

From the repository root, enter the application directory and create a virtual environment:

```bash
cd starter
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Run The Flask App

From `starter/` with the virtual environment active:

```bash
python3 app.py
```

Open <http://127.0.0.1:5000> in a browser.

## Run Tests

Run the exact complete test command from `starter/`:

```bash
python3 -m pytest
```

The test suite covers Sudoku generation and uniqueness, difficulty routing, board validation, hints, completion, and accessibility/styling hooks.

## How To Play

1. Enter an optional player name.
2. Choose Easy, Medium, or Hard. Medium is selected initially.
3. Fill the editable cells with digits 1 through 9. Clearing a cell is allowed.
4. Use Check Puzzle to identify non-empty entries that differ from the solution.
5. Use Hint to fill and lock one correct empty cell.
6. Complete every cell correctly to stop the timer and submit a score.
7. Select New Game to reset the board, timer, hints, and completion state without erasing saved scores.

### Difficulty Behavior

- **Easy:** 40 prefilled cells.
- **Medium:** 32 prefilled cells.
- **Hard:** 26 prefilled cells.

Every difficulty is generated with the same unique-solution guarantee.

### Conflicts, Checking, Hints, Timer, And Completion

Editable entries are checked immediately against all occupied cells in their row, column, and 3x3 box, including prefilled and hinted cells. Conflicts receive visual styling, an invalid-input state, and an accessible status message. The conflict status clears when the duplicate is corrected or removed.

Check Puzzle sends the current board to Flask and highlights incorrect non-empty editable entries. It does not expose the solution and does not mark empty cells incorrect.

Each Hint request returns exactly one correct cell. The cell is filled, locked, styled as hinted, and counted for the current game. The game returns a safe no-empty-cells response when no hint is available.

The timer displays elapsed time as `MM:SS`, starts after a puzzle loads, resets for a successful new game, and stops when the puzzle is correctly completed. It uses timestamp-based elapsed-time calculation so delayed browser intervals do not distort the result.

### Player Name And Leaderboard

A completed puzzle with a non-blank player name creates one leaderboard entry containing the player name, numeric elapsed seconds, formatted time, difficulty, and hints used. Scores sort by fastest numeric time and then by fewest hints. Only the fastest 10 valid entries are displayed and retained.

Scores are stored locally under the versioned key `sudokuLeaderboardV1`. They remain available after page reloads and are not erased by starting a new game. Names are rendered as text, not unsanitized HTML. Malformed or unavailable localStorage is handled without breaking the game.

### Dark Mode And Mobile Usage

Use the Dark mode checkbox in the header. The preference is stored under `sudokuThemeV1`. When no preference is saved, the browser's `prefers-color-scheme` setting provides the initial theme. The board, controls, messages, inputs, and leaderboard use readable theme-aware colors.

The board remains square and scales to the available width. Controls wrap on narrow screens, and the leaderboard uses a horizontal scroll wrapper when its table cannot fit. The layout is intended to remain usable at widths around 320px and above.

## Copilot Screenshot Evidence

The `Screenshots/` directory contains the required evidence:

- `testing_framework_copilot .png`: initial testing framework prompt and response.
- `unique_solution_copilot.png`: unique-solution generation prompt and response.
- `top_10_local_storage_copilot.png`: Top 10 localStorage leaderboard prompt and response.
- `alternating_grid_colors_copilot.png`: alternating 3x3 grid colors prompt and response.
- `copilot_suggestion_evaluation.png`: evaluation and rejection of the SQLite suggestion.

Additional screenshots document difficulty levels, feature validation, timer behavior, leaderboard output, light/dark mode, and mobile views.

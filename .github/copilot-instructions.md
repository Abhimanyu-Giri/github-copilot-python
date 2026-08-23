# GitHub Copilot Instructions

## Project Context

This repository contains a Python Flask Sudoku application being refactored from legacy code. All application code is located in the `starter` directory.

## Development Standards

- Use Python 3 and follow PEP 8 conventions.
- Keep functions small, readable, and focused on one responsibility.
- Use descriptive names for functions, variables, classes, and modules.
- Organize reusable Sudoku logic separately from Flask routes.
- Add type hints and concise docstrings to new Python functions.
- Avoid unnecessary dependencies and duplicated code.
- Preserve existing functionality during refactoring.
- Handle invalid input and unexpected errors consistently.
- Never expose the completed Sudoku solution to the browser unnecessarily.

## Flask Standards

- Keep Flask routes simple and move game logic into dedicated modules.
- Return appropriate JSON responses and HTTP status codes.
- Validate all data received by API endpoints.
- Keep secrets and configuration out of source code.

## Sudoku Requirements

- Generate 9×9 Sudoku puzzles with exactly one solution.
- Support Easy, Medium, and Hard difficulty levels.
- Lock prefilled cells and cells completed using hints.
- Provide immediate visual feedback for conflicting moves.
- The Check feature must highlight entries that differ from the solution.
- A hint must fill one correct empty cell and lock it.
- Show a congratulatory message after successful completion.

## Frontend Standards

- Use semantic HTML and accessible labels.
- Use responsive CSS that works on mobile and desktop.
- Support readable light and dark themes.
- Use alternating colors for the 3×3 Sudoku blocks.
- Keep JavaScript modular and avoid polluting the global scope.
- Persist only the Top 10 results in localStorage.
- Each leaderboard result must contain player name, completion time,
  difficulty, and hints used.

## Testing Standards

- Use pytest for Python tests.
- Add tests for Flask routes and Sudoku logic.
- Keep tests deterministic where random generation is involved.
- Run the complete test suite after every major change.
- Do not weaken or remove tests merely to make them pass.

## Responsible Copilot Use

- Explain significant proposed changes before applying them.
- Make focused changes instead of rewriting unrelated files.
- Clearly identify assumptions and possible edge cases.
- Ask before introducing new frameworks or large dependencies.
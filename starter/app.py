from flask import Flask, render_template, jsonify, request
from typing import Optional
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': None,
    'hints_used': 0,
    'completed': False,
}


def _read_board() -> Optional[list[list[int]]]:
    """Return a valid board from the JSON request, or None for bad input."""
    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    if (
        not isinstance(board, list)
        or len(board) != sudoku_logic.SIZE
        or any(
            not isinstance(row, list)
            or len(row) != sudoku_logic.SIZE
            or any(type(cell) is not int or not 0 <= cell <= 9 for cell in row)
            for row in board
        )
    ):
        return None
    return board

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium').lower()
    if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
        return jsonify({'error': 'Invalid difficulty'}), 400
    clues = sudoku_logic.DIFFICULTY_CLUES[difficulty]
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    CURRENT['hints_used'] = 0
    CURRENT['completed'] = False
    return jsonify({'difficulty': difficulty, 'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    board = _read_board()
    if board is None:
        return jsonify({'error': 'Invalid board'}), 400
    puzzle = CURRENT.get('puzzle')
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if (puzzle is None or puzzle[i][j] == sudoku_logic.EMPTY) and (
                board[i][j] != sudoku_logic.EMPTY
                and board[i][j] != solution[i][j]
            ):
                incorrect.append([i, j])
    completed = not incorrect and all(
        board[i][j] == solution[i][j]
        for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
    )
    if completed:
        CURRENT['completed'] = True
    return jsonify({'completed': completed, 'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def hint():
    """Return one solution cell for the current board without exposing the solution."""
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400
    board = _read_board()
    if board is None:
        return jsonify({'error': 'Invalid board'}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] == sudoku_logic.EMPTY and board[row][col] == sudoku_logic.EMPTY:
                CURRENT['hints_used'] += 1
                return jsonify({
                    'hints_used': CURRENT['hints_used'],
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                })
    return jsonify({
        'hints_used': CURRENT['hints_used'],
        'message': 'No empty cells remain',
    })

if __name__ == '__main__':
    app.run(debug=True)
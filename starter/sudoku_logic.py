import copy
import random

SIZE = 9
EMPTY = 0
MIN_CLUES = 17
DIFFICULTY_CLUES = {
    'easy': 40,
    'medium': 32,
    'hard': 26,
}


def deep_copy(board: list[list[int]]) -> list[list[int]]:
    """Return an independent copy of a Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board() -> list[list[int]]:
    """Create a blank 9x9 Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board: list[list[int]], row: int, col: int, num: int) -> bool:
    """Return whether a number can be placed at a board position."""
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board: list[list[int]]) -> bool:
    """Fill a board with a randomized valid Sudoku solution."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def _validate_board_shape(board: list[list[int]]) -> None:
    """Raise ValueError when a board is not a 9x9 grid of valid values."""
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        raise ValueError('Sudoku board must be a 9x9 grid')
    if any(
        not isinstance(cell, int) or cell < EMPTY or cell > SIZE
        for row in board
        for cell in row
    ):
        raise ValueError('Sudoku cells must be integers from 0 to 9')


def _is_valid_partial_board(board: list[list[int]]) -> bool:
    """Return whether filled values do not conflict in any Sudoku unit."""
    for row in board:
        values = [cell for cell in row if cell != EMPTY]
        if len(values) != len(set(values)):
            return False
    for column in range(SIZE):
        values = [board[row][column] for row in range(SIZE) if board[row][column] != EMPTY]
        if len(values) != len(set(values)):
            return False
    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = [
                board[row][column]
                for row in range(start_row, start_row + 3)
                for column in range(start_col, start_col + 3)
                if board[row][column] != EMPTY
            ]
            if len(values) != len(set(values)):
                return False
    return True


def count_solutions(board: list[list[int]]) -> int:
    """Count solutions, stopping at two to distinguish unique from multiple."""
    _validate_board_shape(board)
    working_board = deep_copy(board)
    if not _is_valid_partial_board(working_board):
        return 0

    def search() -> int:
        best_position = None
        best_candidates = None
        for row in range(SIZE):
            for column in range(SIZE):
                if working_board[row][column] == EMPTY:
                    candidates = [
                        number for number in range(1, SIZE + 1)
                        if is_safe(working_board, row, column, number)
                    ]
                    if not candidates:
                        return 0
                    if best_candidates is None or len(candidates) < len(best_candidates):
                        best_position = (row, column)
                        best_candidates = candidates
                        if len(candidates) == 1:
                            break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_position is None:
            return 1

        row, column = best_position
        solutions = 0
        for number in best_candidates:
            working_board[row][column] = number
            solutions += search()
            working_board[row][column] = EMPTY
            if solutions >= 2:
                return 2
        return solutions

    return search()


def remove_cells(board: list[list[int]], clues: int) -> None:
    """Remove clues while preserving a unique solution for the board."""
    _validate_board_shape(board)
    if not isinstance(clues, int) or not MIN_CLUES <= clues <= SIZE * SIZE:
        raise ValueError(f'clues must be an integer from {MIN_CLUES} to {SIZE * SIZE}')

    positions = [(row, column) for row in range(SIZE) for column in range(SIZE)]
    random.shuffle(positions)
    for row, column in positions:
        if sum(cell != EMPTY for line in board for cell in line) <= clues:
            break
        original = board[row][column]
        if original == EMPTY:
            continue
        board[row][column] = EMPTY
        if count_solutions(board) != 1:
            board[row][column] = original


def generate_puzzle(clues: int = 35) -> tuple[list[list[int]], list[list[int]]]:
    """Generate a puzzle and its solution, with exactly one puzzle solution."""
    if not isinstance(clues, int) or not MIN_CLUES <= clues <= SIZE * SIZE:
        raise ValueError(f'clues must be an integer from {MIN_CLUES} to {SIZE * SIZE}')
    board = create_empty_board()
    if not fill_board(board):
        raise RuntimeError('Unable to generate a complete Sudoku solution')
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    if count_solutions(puzzle) != 1:
        raise RuntimeError('Generated Sudoku puzzle does not have a unique solution')
    return puzzle, solution

import random

import pytest

import sudoku_logic


VALID_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def test_difficulty_settings_define_the_expected_clue_counts():
    assert sudoku_logic.DIFFICULTY_CLUES == {
        'easy': 40,
        'medium': 32,
        'hard': 26,
    }


@pytest.mark.parametrize('difficulty, clues', sudoku_logic.DIFFICULTY_CLUES.items())
def test_each_difficulty_generates_a_unique_puzzle(difficulty, clues):
    random.seed(19)

    puzzle, solution = sudoku_logic.generate_puzzle(clues)

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
    assert all(
        puzzle_cell == sudoku_logic.EMPTY or puzzle_cell == solution_cell
        for puzzle_row, solution_row in zip(puzzle, solution)
        for puzzle_cell, solution_cell in zip(puzzle_row, solution_row)
    )


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_is_independent():
    board = [[1]]

    copied_board = sudoku_logic.deep_copy(board)
    copied_board[0][0] = 2

    assert board == [[1]]


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 1, 1, 6)


def test_count_solutions_returns_one_for_a_completed_board():
    assert sudoku_logic.count_solutions(VALID_BOARD) == 1


def test_count_solutions_stops_at_two_for_a_board_with_many_solutions():
    assert sudoku_logic.count_solutions(sudoku_logic.create_empty_board()) == 2


def test_count_solutions_returns_zero_for_an_invalid_board():
    board = sudoku_logic.deep_copy(VALID_BOARD)
    board[0][1] = board[0][0]

    assert sudoku_logic.count_solutions(board) == 0


def test_fill_board_creates_a_complete_valid_board():
    random.seed(7)
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert all(sorted(row) == list(range(1, 10)) for row in board)
    assert all(
        sorted(board[row][column] for row in range(9)) == list(range(1, 10))
        for column in range(9)
    )


def test_remove_cells_leaves_requested_number_of_clues():
    board = sudoku_logic.deep_copy(VALID_BOARD)

    random.seed(11)
    sudoku_logic.remove_cells(board, clues=30)

    assert sum(cell != sudoku_logic.EMPTY for row in board for cell in row) == 30


def test_generate_puzzle_is_seeded_and_matches_its_solution():
    random.seed(19)
    first_puzzle, first_solution = sudoku_logic.generate_puzzle(clues=35)
    random.seed(19)
    second_puzzle, second_solution = sudoku_logic.generate_puzzle(clues=35)

    assert (first_puzzle, first_solution) == (second_puzzle, second_solution)
    assert all(sorted(row) == list(range(1, 10)) for row in first_solution)
    assert sum(cell != sudoku_logic.EMPTY for row in first_puzzle for cell in row) == 35
    assert sudoku_logic.count_solutions(first_puzzle) == 1
    assert all(
        puzzle_cell == sudoku_logic.EMPTY or puzzle_cell == solution_cell
        for puzzle_row, solution_row in zip(first_puzzle, first_solution)
        for puzzle_cell, solution_cell in zip(puzzle_row, solution_row)
    )

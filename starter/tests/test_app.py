import copy

import pytest

import app as app_module
import sudoku_logic


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client
    app_module.CURRENT.update(
        puzzle=None,
        solution=None,
        difficulty=None,
        hints_used=0,
        completed=False,
    )


def test_index_route_renders_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.content_type.startswith('text/html')
    assert b'id="difficulty"' in response.data
    assert b'<option value="medium" selected>' in response.data
    assert b'id="timer"' in response.data
    assert b'aria-live="off"' in response.data


def test_new_route_returns_generated_puzzle_and_stores_game(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = copy.deepcopy(puzzle)
    received_clues = []

    def controlled_generator(clues):
        received_clues.append(clues)
        return puzzle, solution

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle',
        controlled_generator,
    )

    response = client.get('/new?difficulty=easy')

    assert response.status_code == 200
    assert response.get_json() == {'difficulty': 'easy', 'puzzle': puzzle}
    assert received_clues == [40]
    assert app_module.CURRENT == {
        'puzzle': puzzle,
        'solution': solution,
        'difficulty': 'easy',
        'hints_used': 0,
        'completed': False,
    }


def test_new_route_defaults_to_medium(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = copy.deepcopy(puzzle)
    received_clues = []

    def controlled_generator(clues):
        received_clues.append(clues)
        return puzzle, solution

    monkeypatch.setattr(app_module.sudoku_logic, 'generate_puzzle', controlled_generator)

    response = client.get('/new')

    assert response.status_code == 200
    assert response.get_json()['difficulty'] == 'medium'
    assert received_clues == [32]


def test_new_route_resets_hints_and_completion_state(client, monkeypatch):
    puzzle = sudoku_logic.create_empty_board()
    solution = copy.deepcopy(puzzle)
    app_module.CURRENT.update(hints_used=4, completed=True)

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle',
        lambda clues: (puzzle, solution),
    )

    response = client.get('/new?difficulty=hard')

    assert response.status_code == 200
    assert app_module.CURRENT['hints_used'] == 0
    assert app_module.CURRENT['completed'] is False


def test_new_route_rejects_invalid_difficulty(client):
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid difficulty'}


def test_check_route_requires_an_active_game(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_route_rejects_invalid_board_data(client):
    app_module.CURRENT['solution'] = sudoku_logic.create_empty_board()

    response = client.post('/check', json={'board': [[1]]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid board'}


def test_check_route_reports_cells_that_differ_from_solution(client):
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    board = copy.deepcopy(solution)
    board[0][0] = 9
    app_module.CURRENT['solution'] = solution

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'completed': False, 'incorrect': [[0, 0]]}


def test_check_route_marks_only_a_fully_correct_board_as_completed(client):
    solution = sudoku_logic.create_empty_board()
    puzzle = sudoku_logic.create_empty_board()
    app_module.CURRENT.update(puzzle=puzzle, solution=solution)

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'completed': True, 'incorrect': []}
    assert app_module.CURRENT['completed'] is True


def test_hint_route_returns_one_cell_and_tracks_hints(client):
    solution = [row[:] for row in sudoku_logic.create_empty_board()]
    solution[0][0] = 5
    puzzle = sudoku_logic.create_empty_board()
    app_module.CURRENT.update(puzzle=puzzle, solution=solution)

    response = client.post('/hint', json={'board': puzzle})

    assert response.status_code == 200
    assert response.get_json() == {
        'hints_used': 1,
        'row': 0,
        'col': 0,
        'value': 5,
    }
    assert app_module.CURRENT['hints_used'] == 1


def test_hint_route_returns_safe_response_when_no_empty_cells_remain(client):
    solution = [[5 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]
    puzzle = [row[:] for row in solution]
    app_module.CURRENT.update(puzzle=puzzle, solution=solution)

    response = client.post('/hint', json={'board': puzzle})

    assert response.status_code == 200
    assert response.get_json() == {
        'hints_used': 0,
        'message': 'No empty cells remain',
    }

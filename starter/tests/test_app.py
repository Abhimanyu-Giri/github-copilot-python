import copy

import pytest

import app as app_module
import sudoku_logic


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client
    app_module.CURRENT.update(puzzle=None, solution=None)


def test_index_route_renders_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.content_type.startswith('text/html')


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

    response = client.get('/new?clues=40')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': puzzle}
    assert received_clues == [40]
    assert app_module.CURRENT == {'puzzle': puzzle, 'solution': solution}


def test_check_route_requires_an_active_game(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


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
    assert response.get_json() == {'incorrect': [[0, 0]]}

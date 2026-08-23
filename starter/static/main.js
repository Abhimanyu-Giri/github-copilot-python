// Client-side rendering and interaction for the Flask-backed Sudoku
(() => {
const SIZE = 9;
let puzzle = [];
let gameCompleted = false;

const timer = (() => {
  let intervalId = null;
  let startedAt = null;
  let elapsedSeconds = 0;

  function render() {
    const timerElement = document.getElementById('timer');
    const minutes = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
    const seconds = (elapsedSeconds % 60).toString().padStart(2, '0');
    timerElement.innerText = `${minutes}:${seconds}`;
  }

  function update() {
    elapsedSeconds = Math.floor((performance.now() - startedAt) / 1000);
    render();
  }

  return {
    reset() {
      if (intervalId !== null) clearInterval(intervalId);
      elapsedSeconds = 0;
      startedAt = performance.now();
      render();
      intervalId = setInterval(update, 1000);
    },
    stop() {
      if (intervalId === null) return;
      update();
      clearInterval(intervalId);
      intervalId = null;
    }
  };
})();

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateConflicts();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (!res.ok) {
    document.getElementById('message').innerText = data.error || 'Unable to start a new game.';
    return;
  }
  gameCompleted = false;
  renderPuzzle(data.puzzle);
  document.getElementById('difficulty').value = data.difficulty;
  document.getElementById('difficulty-display').innerText =
    data.difficulty.charAt(0).toUpperCase() + data.difficulty.slice(1);
  document.getElementById('hints-used').innerText = 'Hints used: 0';
  document.getElementById('message').innerText = '';
  updateConflicts();
  timer.reset();
}

function readBoard(inputs) {
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const val = inputs[i * SIZE + j].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function updateConflicts() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let index = 0; index < inputs.length; index++) {
    const input = inputs[index];
    if (!input.disabled) {
      input.classList.remove('conflict');
      input.setAttribute('aria-invalid', 'false');
    }
  }
  for (let first = 0; first < inputs.length; first++) {
    if (inputs[first].disabled || !inputs[first].value) continue;
    const firstRow = Math.floor(first / SIZE);
    const firstCol = first % SIZE;
    for (let second = first + 1; second < inputs.length; second++) {
      if (inputs[second].disabled || inputs[second].value !== inputs[first].value) continue;
      const secondRow = Math.floor(second / SIZE);
      const secondCol = second % SIZE;
      const sameBox = Math.floor(firstRow / 3) === Math.floor(secondRow / 3) &&
        Math.floor(firstCol / 3) === Math.floor(secondCol / 3);
      if (firstRow === secondRow || firstCol === secondCol || sameBox) {
        inputs[first].classList.add('conflict');
        inputs[second].classList.add('conflict');
        inputs[first].setAttribute('aria-invalid', 'true');
        inputs[second].setAttribute('aria-invalid', 'true');
      }
    }
  }
}

async function checkPuzzle() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = readBoard(inputs);
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (!res.ok || data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (data.completed && !gameCompleted) {
    gameCompleted = true;
    timer.stop();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = 'No incorrect entries found. Complete the remaining cells.';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some non-empty cells are incorrect.';
  }
}

async function requestHint() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: readBoard(inputs)})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (!res.ok || data.error) {
    msg.innerText = data.error || 'Unable to provide a hint.';
    return;
  }
  document.getElementById('hints-used').innerText = `Hints used: ${data.hints_used}`;
  if (data.row === undefined) {
    msg.innerText = data.message;
    return;
  }
  const input = inputs[data.row * SIZE + data.col];
  input.value = data.value;
  input.disabled = true;
  input.className = 'sudoku-cell hinted';
  input.setAttribute('aria-invalid', 'false');
  if (Array.from(inputs).every((cell) => cell.value)) {
    await checkPuzzle();
  } else {
    msg.innerText = 'One correct cell was filled and locked.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-puzzle').addEventListener('click', checkPuzzle);
  document.getElementById('hint').addEventListener('click', requestHint);
  // initialize
  newGame();
});
})();
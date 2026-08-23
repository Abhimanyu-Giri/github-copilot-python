// Client-side rendering and interaction for the Flask-backed Sudoku
(() => {
const SIZE = 9;
let puzzle = [];
let gameCompleted = false;
let scoreSubmitted = false;
let hintsUsed = 0;

const theme = (() => {
  const STORAGE_KEY = 'sudokuThemeV1';
  const toggle = document.getElementById('theme-toggle');

  function apply(value) {
    document.documentElement.dataset.theme = value;
    toggle.checked = value === 'dark';
  }

  function initialize() {
    let savedTheme = null;
    try {
      savedTheme = window.localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      savedTheme = null;
    }
    const initialTheme = savedTheme === 'dark' || savedTheme === 'light'
      ? savedTheme
      : (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    apply(initialTheme);
    toggle.addEventListener('change', () => {
      const value = toggle.checked ? 'dark' : 'light';
      apply(value);
      try {
        window.localStorage.setItem(STORAGE_KEY, value);
      } catch (error) {
        // Theme still applies for this session when storage is unavailable.
      }
    });
  }

  return {initialize};
})();

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
    },
    getElapsedSeconds() {
      return elapsedSeconds;
    }
  };
})();

const leaderboard = (() => {
  const STORAGE_KEY = 'sudokuLeaderboardV1';
  const MAX_ENTRIES = 10;
  const validDifficulties = new Set(['easy', 'medium', 'hard']);

  function isValidEntry(entry) {
    return entry && typeof entry.playerName === 'string' && entry.playerName.trim() &&
      Number.isFinite(entry.elapsedSeconds) && entry.elapsedSeconds >= 0 &&
      typeof entry.formattedTime === 'string' && validDifficulties.has(entry.difficulty) &&
      Number.isInteger(entry.hintsUsed) && entry.hintsUsed >= 0;
  }

  function read() {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      const entries = stored ? JSON.parse(stored) : [];
      return Array.isArray(entries) ? entries.filter(isValidEntry) : [];
    } catch (error) {
      return [];
    }
  }

  function sortEntries(entries) {
    return entries.sort((first, second) =>
      first.elapsedSeconds - second.elapsedSeconds || first.hintsUsed - second.hintsUsed
    ).slice(0, MAX_ENTRIES);
  }

  function render() {
    const entries = sortEntries(read());
    const table = document.getElementById('leaderboard-table');
    const empty = document.getElementById('leaderboard-empty');
    const body = document.getElementById('leaderboard-body');
    body.replaceChildren();
    entries.forEach((entry, index) => {
      const row = document.createElement('tr');
      [index + 1, entry.playerName, entry.formattedTime, entry.difficulty, entry.hintsUsed]
        .forEach((value) => {
          const cell = document.createElement('td');
          cell.textContent = String(value);
          row.appendChild(cell);
        });
      body.appendChild(row);
    });
    table.hidden = entries.length === 0;
    empty.hidden = entries.length !== 0;
  }

  function add(entry) {
    const entries = sortEntries([...read(), entry]);
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
    } catch (error) {
      render();
      return false;
    }
    render();
    return true;
  }

  return {add, render};
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
      const blockParity = (Math.floor(i / 3) + Math.floor(j / 3)) % 2;
      inp.className = `sudoku-cell block-${blockParity ? 'odd' : 'even'}`;
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
  scoreSubmitted = false;
  hintsUsed = 0;
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

function submitScore() {
  if (scoreSubmitted) return true;
  const nameInput = document.getElementById('player-name');
  const playerName = nameInput.value.trim();
  const msg = document.getElementById('message');
  if (!playerName) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Enter your player name to save your completed time.';
    nameInput.focus();
    return false;
  }
  const difficulty = document.getElementById('difficulty').value;
  const elapsedSeconds = timer.getElapsedSeconds();
  const minutes = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
  const seconds = (elapsedSeconds % 60).toString().padStart(2, '0');
  if (leaderboard.add({
    playerName,
    elapsedSeconds,
    formattedTime: `${minutes}:${seconds}`,
    difficulty,
    hintsUsed
  })) {
    scoreSubmitted = true;
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! Your time was added to the leaderboard.';
  }
  return scoreSubmitted;
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
    const row = Math.floor(idx / SIZE);
    const col = idx % SIZE;
    const blockParity = (Math.floor(row / 3) + Math.floor(col / 3)) % 2;
    inp.className = `sudoku-cell block-${blockParity ? 'odd' : 'even'}`;
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (data.completed && !gameCompleted) {
    gameCompleted = true;
    timer.stop();
    submitScore();
  } else if (data.completed) {
    submitScore();
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
  hintsUsed = data.hints_used;
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
  theme.initialize();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-puzzle').addEventListener('click', checkPuzzle);
  document.getElementById('hint').addEventListener('click', requestHint);
  leaderboard.render();
  // initialize
  newGame();
});
})();
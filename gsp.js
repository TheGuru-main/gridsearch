// ── Keyboard layout ─────────────────────────────────
const KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"];
const keyMap = new Map();
for (let r = 0; r < KEYBOARD_ROWS.length; r++) {
  for (let c = 0; c < KEYBOARD_ROWS[r].length; c++) {
    keyMap.set(KEYBOARD_ROWS[r][c], { L: r, S: c });
  }
}

// ── Core GSP functions ──────────────────────────────
function calculate_lsum(word) {
  let sum = 0;
  for (const ch of word.toLowerCase()) if (keyMap.has(ch)) sum += keyMap.get(ch).L;
  return sum;
}

function calculate_ssum(word) {
  let sum = 0;
  for (const ch of word.toLowerCase()) if (keyMap.has(ch)) sum += keyMap.get(ch).S;
  return sum;
}

function first_letter_index(word) {
  if (!word) return 0;
  const c = word.toLowerCase().charCodeAt(0) - 97;
  return (c >= 0 && c < 26) ? c : 0;
}

function gsp_place(Lsum, Ssum, c, K = 5, D = 8, C = 26, R = 64) {
  const start_row = ((Lsum + Ssum - 1) % R + R) % R + 1;
  const cells = [];
  for (let k = 0; k < K; k++) {
    const row = ((start_row - 1 + k * D) % R + R) % R + 1;
    const col = (c + k) % C;
    cells.push({ col, row, k });
  }
  return { start_row, primary_cell: cells[0], cells };
}

function elasticCloud(L, S, c, radius = 1, firstLetterRadius = 1, C = 26, R = 64) {
  const cloud = new Set();
  for (let dc = -firstLetterRadius; dc <= firstLetterRadius; dc++) {
    const c2 = (c + dc + C) % C;
    for (let dL = -radius; dL <= radius; dL++) {
      for (let dS = -radius; dS <= radius; dS++) {
        if (dL === 0 && dS === 0 && dc === 0) continue;
        const L2 = L + dL, S2 = S + dS;
        const startRow = ((L2 + S2 - 1) % R + R) % R + 1;
        cloud.add(`${c2},${startRow}`);
      }
    }
  }
  const baseStartRow = ((L + S - 1) % R + R) % R + 1;
  cloud.add(`${c % C},${baseStartRow}`);
  return Array.from(cloud).map(s => {
    const [col, row] = s.split(',').map(Number);
    return { col, row };
  });
}

module.exports = { calculate_lsum, calculate_ssum, first_letter_index, gsp_place, elasticCloud };
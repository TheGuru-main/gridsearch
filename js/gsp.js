(function () {
    function normalizeName(name) { return (name || '').toLowerCase().replace(/[^a-z]/g, ''); }
    function nameLength(name) { return normalizeName(name).length; }
    function digitSum(text) { return (text || '').split('').filter(ch => /\d/.test(ch)).reduce((s, ch) => s + parseInt(ch, 10), 0); }

    // OpenBox grid: 4 columns (categories), row always 1
    function objectPlacement(category) {
        const c = OpenBox.CONFIG.CATEGORY_COL[category] ?? 3;
        return { row: 1, col: c };
    }

    // User startrow (used for messages and squads)
    function userStartRow(fullName, phone) {
        const L = nameLength(fullName);
        const S = digitSum(phone);
        return ((L + S - 1) % 64) + 1;
    }

    function getFileIcon(category) {
        const icons = { app: '📱', game: '🎮', video: '🎬', other: '📄' };
        return icons[category] || '📄';
    }

    OpenBox.GSP = { normalizeName, nameLength, digitSum, objectPlacement, userStartRow, getFileIcon };
})();
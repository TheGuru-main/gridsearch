(function () {
    async function refresh() {
        const r = await OpenBox.API.wallet();
        if (!r.ok) return;
        OpenBox.App.currentUser.byflints = r.data.balance;
        updateUI(r.data.balance, r.data.ledger);
    }

    function updateUI(balance, ledger) {
        const bal = document.getElementById('walletBalanceDisplay');
        if (bal) bal.textContent = Number(balance || 0).toFixed(2);
        const hist = document.getElementById('transactionHistory');
        if (!hist) return;
        if (!ledger || !ledger.length) {
            hist.innerHTML = '<p class="hint">No transactions yet.</p>';
            return;
        }
        hist.innerHTML = ledger.map(e => `
            <div class="ledger-row">
                <span>${e.reason || ''}</span>
                <span class="amt ${e.amount >= 0 ? 'positive' : 'negative'}">
                    ${e.amount >= 0 ? '+' : ''}${e.amount}
                </span>
            </div>
        `).join('');
    }

    function show() {
        OpenBox.UI.showWorkspace('workspaceWallet');
        refresh();
    }

    OpenBox.Wallet = { show, refresh };
})();
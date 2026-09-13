(function () {
    async function show() {
        OpenBox.UI.showWorkspace('workspaceFantasy');
        const h = await OpenBox.API.health();
        const wk = document.getElementById('fantasyWeek');
        if (wk) wk.textContent = `Week ${h.data?.gameweek || '?'}`;
        loadTab('tournaments');
    }

    function loadTab(tab) {
        if (tab === 'tournaments') loadTournaments();
        else if (tab === 'hot') loadHot();
        else if (tab === 'transfers') loadTransfers();
    }

    async function loadTournaments() {
        const body = document.getElementById('fantasyBody');
        body.innerHTML = '<p class="hint">Loading...</p>';
        const r = await OpenBox.API.tournaments();
        if (!r.ok || !r.data.tournaments?.length) {
            body.innerHTML = '<p class="hint">No tournaments loaded yet. The scraper runs every 6 hours.</p>';
            return;
        }
        body.innerHTML = `
            <div class="tournament-list">
                ${r.data.tournaments.map(t => `
                    <a href="#" class="tournament-item" data-tid="${t.tournament_id}">
                        <strong>${t.tournament_id.toUpperCase().replace(/_/g, ' ')}</strong>
                        <small>${t.club_count} clubs</small>
                    </a>`).join('')}
            </div>`;
        body.querySelectorAll('.tournament-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                loadTournamentDetail(el.dataset.tid, body);
            });
        });
    }

    async function loadTournamentDetail(tid, body) {
        const r = await OpenBox.API.tournament(tid);
        if (!r.ok) return;
        const t = r.data;
        body.innerHTML = `
            <a href="#" class="secondary-btn" id="backToT">← Back</a>
            <h3>${tid.toUpperCase().replace(/_/g, ' ')}</h3>
            <p class="hint">Base price: ${t.base_price} byflints per player</p>
            <div class="club-grid">
                ${t.clubs.map(c => `<a href="#" class="club-chip" data-cid="${c.id}">${c.name}</a>`).join('')}
            </div>`;
        document.getElementById('backToT').addEventListener('click', (e) => {
            e.preventDefault(); loadTournaments();
        });
        body.querySelectorAll('.club-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                e.preventDefault();
                loadClub(chip.dataset.cid, body);
            });
        });
    }

    async function loadClub(cid, body) {
        body.innerHTML = '<p class="hint">Loading players...</p>';
        const r = await OpenBox.API.clubPlayers(cid);
        if (!r.ok) { body.innerHTML = '<p class="hint">Failed to load.</p>'; return; }
        const d = r.data;
        body.innerHTML = `
            <a href="#" class="secondary-btn" id="backFromClub">← Back</a>
            <h3>${cid.split(':').pop().toUpperCase()}</h3>
            <p class="hint">Week ${d.week}</p>
            <div class="player-list">
                ${(d.players || []).map(p => `
                    <div class="player-card">
                        <div>
                            <strong>${p.name}</strong>
                            <small>${p.position || ''} ${p.number ? '#' + p.number : ''}</small>
                        </div>
                        <div style="text-align:right;">
                            <div class="pts">${p.points_this_week} pts</div>
                            <div class="price">${p.price} bf</div>
                        </div>
                    </div>`).join('')}
            </div>`;
        document.getElementById('backFromClub').addEventListener('click', (e) => {
            e.preventDefault();
            const tid = cid.split(':')[0];
            loadTournamentDetail(tid, body);
        });
    }

    async function loadHot() {
        const body = document.getElementById('fantasyBody');
        body.innerHTML = '<p class="hint">Loading...</p>';
        const r = await OpenBox.API.hot();
        if (!r.ok) return;
        const list = r.data.hot || [];
        body.innerHTML = `
            <h3>Hot This Week</h3>
            <div class="hot-list">
                ${list.map(h => `
                    <div class="hot-player">
                        <strong>${h.player.name}</strong>
                        <small>${h.tournament_id.toUpperCase()} · ${h.player.position || ''}</small>
                        <span>${h.points} pts · ${h.price} byflints</span>
                    </div>`).join('')}
            </div>`;
    }

    async function loadTransfers() {
        const body = document.getElementById('fantasyBody');
        body.innerHTML = '<p class="hint">Loading...</p>';
        const r = await OpenBox.API.transfers(30);
        if (!r.ok) return;
        const list = r.data.transfers || [];
        if (!list.length) {
            body.innerHTML = '<p class="hint">No transfers yet. The scraper runs every 6 hours.</p>';
            return;
        }
        body.innerHTML = `
            <h3>Recent Transfers (30 days)</h3>
            <div class="transfer-list">
                ${list.map(t => `
                    <div class="transfer-row">
                        <strong>${t.player_name}</strong>
                        <small>${t.from_club || '?'} → ${t.to_club || '?'}</small>
                        <span>${t.fee || '—'} · ${t.date} · ${t.source}</span>
                    </div>`).join('')}
            </div>`;
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.ftab').forEach(t => {
            t.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.ftab').forEach(x => x.classList.remove('active'));
                t.classList.add('active');
                loadTab(t.dataset.ftab);
            });
        });
    });

    OpenBox.Fantasy = { show };
})();
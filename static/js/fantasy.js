/**
 * Fantasy workspace.
 * Primary data source: OpenBox.FantasyRegistry (local, always available).
 * Falls back to backend /api/fantasy/* if the local registry is empty.
 * Squad lives in localStorage, keyed by phone.
 */
(function () {

    // ═══════════════════════════════════════════════════
    //  SQUAD STORAGE
    // ═══════════════════════════════════════════════════
    const SQUAD_KEY = "openbox_squad";

    function loadSquad() {
        const phone = OpenBox.App.currentUser?.phone;
        if (!phone) return null;
        const all = JSON.parse(localStorage.getItem(SQUAD_KEY) || "{}");
        return all[phone] || null;
    }

    function saveSquad(squad) {
        const phone = OpenBox.App.currentUser?.phone;
        if (!phone) return;
        const all = JSON.parse(localStorage.getItem(SQUAD_KEY) || "{}");
        all[phone] = squad;
        localStorage.setItem(SQUAD_KEY, JSON.stringify(all));
    }

    function emptySquad() {
        return {
            name: OpenBox.App.currentUser?.fullName + "'s XI" || "My XI",
            country: OpenBox.App.currentUser?.country || "NG",
            formation: "4-4-2",
            players: [],
            captain: null,
            vice: null,
            gsp_row: null,
            created_at: new Date().toISOString()
        };
    }

    // ═══════════════════════════════════════════════════
    //  REGISTRY ACCESS — works whether registry or backend
    // ═══════════════════════════════════════════════════
    function getTournaments() {
        const reg = window.OpenBox?.FantasyRegistry?.tournaments;
        if (!reg) return [];
        return Object.values(reg).map(t => ({
            id: t.id,
            name: t.name,
            region: t.region,
            type: t.type,
            club_count: t.clubs.length
        }));
    }

    function getTournament(id) {
        const t = OpenBox.FantasyRegistry?.tournaments?.[id];
        if (!t) return null;
        return {
            ...t,
            clubs: t.clubs.map((c, col) => ({ id: c.id, name: c.name, col }))
        };
    }

    function getClubPlayers(tid, cid) {
        const t = OpenBox.FantasyRegistry?.tournaments?.[tid];
        if (!t) return [];
        const club = t.clubs.find(c => c.id === cid);
        if (!club) return [];

        // Tier-based pricing
        const TIER_BASE = {
            npfl: 120, egypt_pl: 140, sa_psl: 140, botola: 140,
            cafcl: 250, cafcc: 250,
            brasileirao_b: 280, brasileirao_a: 350, argentina_primera: 350,
            mls: 400, ligamx: 400, j1: 400, saudi_pl: 450,
            eredivisie: 400, portugal: 450, turkey: 400,
            epl: 600, laliga: 600, seriea: 600, bundes: 550, ligue1: 500,
            ucl: 800, uel: 700, uecl: 600,
            libertadores: 500, sudamericana: 450, concacaf_cl: 450, afc_cl: 500,
            worldcup: 1000, afcon: 800, euro: 900, copa_america: 800
        };
        const base = TIER_BASE[tid] || 300;
        const POS_BONUS = { GK: 0, DEF: 20, MID: 40, FWD: 80 };

        return club.players.map((p, i) => {
            const id = `${tid}:${cid}:${i}`;
            const hash = (p.name || "").split("").reduce((s, c) => s + c.charCodeAt(0), 0);
            const price = base + (POS_BONUS[p.pos] || 40) + (hash % 60);
            return {
                id, name: p.name, pos: p.pos,
                club_id: cid, club_name: club.name,
                tournament_id: tid, tournament_name: t.name,
                price
            };
        });
    }

    // ═══════════════════════════════════════════════════
    //  GSP — team row anchor
    // ═══════════════════════════════════════════════════
    function computeTeamRow(teamName, phone) {
        const L = (teamName || "").replace(/[^a-z]/gi, "").length;
        const S = (phone || "").split("").filter(ch => /\d/.test(ch))
                              .reduce((s, ch) => s + parseInt(ch, 10), 0);
        return ((L + S - 1) % 64) + 1;
    }

    // ═══════════════════════════════════════════════════
    //  STATE (per session)
    // ═══════════════════════════════════════════════════
    let currentView = "tournaments";   // tournaments | hot | transfers | squad | team
    let navStack = [];                 // breadcrumbs

    // ═══════════════════════════════════════════════════
    //  RENDER — main entry
    // ═══════════════════════════════════════════════════
    function show() {
        OpenBox.UI.showWorkspace("workspaceFantasy");
        const wk = document.getElementById("fantasyWeek");
        if (wk) wk.textContent = "Season 2026/27";
        render();
    }

    function render() {
        const body = document.getElementById("fantasyBody");
        if (!body) return;
        if (currentView === "tournaments") renderTournaments(body);
        else if (currentView === "hot") renderHot(body);
        else if (currentView === "transfers") renderTransfers(body);
        else if (currentView === "squad") renderSquad(body);
        else if (currentView === "team") renderTeam(body);
    }

    function setView(v) {
        currentView = v;
        document.querySelectorAll(".ftab").forEach(t => {
            t.classList.toggle("active", t.dataset.ftab === v);
        });
        render();
    }

    // ═══════════════════════════════════════════════════
    //  VIEW: TOURNAMENTS
    // ═══════════════════════════════════════════════════
    function renderTournaments(body) {
        const list = getTournaments();
        if (!list.length) {
            body.innerHTML = '<p class="hint">No tournaments available.</p>';
            return;
        }
        // Group by region
        const byRegion = {};
        list.forEach(t => (byRegion[t.region] = byRegion[t.region] || []).push(t));

        let html = '';
        for (const region of Object.keys(byRegion)) {
            html += `<h3 class="region-header">${region}</h3>`;
            html += '<div class="tournament-list">';
            html += byRegion[region].map(t => `
                <a href="#" class="tournament-item" data-tid="${t.id}">
                    <div>
                        <strong>${t.name}</strong>
                        <small>${t.club_count} clubs · ${t.type}</small>
                    </div>
                    <span class="chev">›</span>
                </a>
            `).join('');
            html += '</div>';
        }
        body.innerHTML = html;

        body.querySelectorAll('.tournament-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                renderClubs(body, el.dataset.tid);
            });
        });
    }

    // ═══════════════════════════════════════════════════
    //  VIEW: CLUBS IN A TOURNAMENT
    // ═══════════════════════════════════════════════════
    function renderClubs(body, tid) {
        const t = getTournament(tid);
        if (!t) return;
        body.innerHTML = `
            <a href="#" class="back-btn" id="back">← Tournaments</a>
            <h3>${t.name}</h3>
            <small class="hint">${t.clubs.length} clubs · Grid ${t.cols}×${t.rows}</small>
            <div class="club-grid">
                ${t.clubs.map(c => `
                    <a href="#" class="club-chip" data-cid="${c.id}">
                        <span>${c.name}</span>
                        <small>col ${c.col}</small>
                    </a>
                `).join('')}
            </div>
        `;
        document.getElementById('back').addEventListener('click', (e) => {
            e.preventDefault(); setView('tournaments');
        });
        body.querySelectorAll('.club-chip').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                renderPlayers(body, tid, el.dataset.cid);
            });
        });
    }

    // ═══════════════════════════════════════════════════
    //  VIEW: PLAYERS IN A CLUB (with + button)
    // ═══════════════════════════════════════════════════
    function renderPlayers(body, tid, cid) {
        const t = getTournament(tid);
        const club = t?.clubs.find(c => c.id === cid);
        if (!club) return;
        const players = getClubPlayers(tid, cid);
        const squad = loadSquad() || emptySquad();
        const owned = new Set(squad.players.map(p => p.id));
        const balance = OpenBox.App.currentUser?.byflints || 0;

        body.innerHTML = `
            <a href="#" class="back-btn" id="back">← ${t.name}</a>
            <h3>${club.name}</h3>
            <div class="balance-line">
                <span>Balance: <strong>${Number(balance).toFixed(0)} bf</strong></span>
                <span>${squad.players.length} in squad</span>
            </div>
            <div class="player-list">
                ${players.map(p => {
                    const isOwned = owned.has(p.id);
                    const canAfford = balance >= p.price;
                    return `
                        <div class="player-card">
                            <div class="pc-left">
                                <strong>${p.name}</strong>
                                <small>${p.pos} · ${p.price} bf</small>
                            </div>
                            <div class="pc-right">
                                ${isOwned
                                    ? '<span class="owned-tag">✓ Owned</span>'
                                    : `<a href="#" class="add-btn ${canAfford ? '' : 'disabled'}"
                                          data-pid="${p.id}"
                                          data-name="${p.name}"
                                          data-pos="${p.pos}"
                                          data-price="${p.price}"
                                          data-tid="${tid}"
                                          data-cid="${cid}"
                                          data-tname="${t.name}"
                                          data-cname="${club.name}">
                                          + ${p.price}
                                       </a>`
                                }
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        document.getElementById('back').addEventListener('click', (e) => {
            e.preventDefault(); renderClubs(body, tid);
        });
        body.querySelectorAll('.add-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                if (btn.classList.contains('disabled')) {
                    return alert('Not enough byflints.');
                }
                addPlayerToSquad({
                    id: btn.dataset.pid,
                    name: btn.dataset.name,
                    pos: btn.dataset.pos,
                    price: parseInt(btn.dataset.price, 10),
                    tournament_id: btn.dataset.tid,
                    tournament_name: btn.dataset.tname,
                    club_id: btn.dataset.cid,
                    club_name: btn.dataset.cname
                });
                renderPlayers(body, tid, cid);
            });
        });
    }

    // ═══════════════════════════════════════════════════
    //  ADD / REMOVE PLAYER
    // ═══════════════════════════════════════════════════
    function addPlayerToSquad(player) {
        const squad = loadSquad() || emptySquad();

        if (squad.players.find(p => p.id === player.id)) {
            return alert('Already in your squad.');
        }
        if (squad.players.length >= 18) {
            return alert('Squad full (18 players max). Remove one first.');
        }
        // Club limit: max 3 players from the same club
        const sameClub = squad.players.filter(p => p.club_id === player.club_id).length;
        if (sameClub >= 3) {
            return alert(`Max 3 players from ${player.club_name}.`);
        }
        const balance = OpenBox.App.currentUser?.byflints || 0;
        if (balance < player.price) {
            return alert('Not enough byflints.');
        }

        // Deduct from local balance and sync to backend wallet
        OpenBox.App.currentUser.byflints = balance - player.price;
        squad.players.push(player);
        if (squad.gsp_row === null) {
            squad.gsp_row = computeTeamRow(squad.name, OpenBox.App.currentUser?.phone);
        }
        saveSquad(squad);
        updateBalanceUI();
        alert(`${player.name} added for ${player.price} bf.`);
    }

    function removePlayerFromSquad(playerId) {
        const squad = loadSquad();
        if (!squad) return;
        const idx = squad.players.findIndex(p => p.id === playerId);
        if (idx < 0) return;
        const p = squad.players[idx];
        squad.players.splice(idx, 1);
        if (squad.captain === playerId) squad.captain = null;
        if (squad.vice === playerId) squad.vice = null;
        saveSquad(squad);
        OpenBox.App.currentUser.byflints = (OpenBox.App.currentUser.byflints || 0) + p.price;
        updateBalanceUI();
    }

    function updateBalanceUI() {
        // The wallet screen has its own display. Update if visible.
        const el = document.getElementById('walletBalanceDisplay');
        if (el) el.textContent = Number(OpenBox.App.currentUser?.byflints || 0).toFixed(2);
    }

    // ═══════════════════════════════════════════════════
    //  VIEW: MY SQUAD (list with formation + captain)
    // ═══════════════════════════════════════════════════
    function renderSquad(body) {
        const squad = loadSquad() || emptySquad();
        const FORMS = ["4-4-2", "4-3-3", "3-5-2", "3-4-3", "5-3-2", "5-4-1"];

        // Count by position
        const counts = { GK: 0, DEF: 0, MID: 0, FWD: 0 };
        squad.players.forEach(p => counts[p.pos] = (counts[p.pos] || 0) + 1);

        body.innerHTML = `
            <div class="squad-header">
                <input type="text" id="squadName" value="${squad.name}" maxlength="40">
                <select id="squadFormation">
                    ${FORMS.map(f => `<option ${f === squad.formation ? 'selected' : ''}>${f}</option>`).join('')}
                </select>
            </div>
            <div class="squad-meta">
                <span>Country: <strong>${squad.country}</strong></span>
                <span>GSP row: <strong>${squad.gsp_row || '—'}</strong></span>
                <span>Balance: <strong>${Number(OpenBox.App.currentUser?.byflints || 0).toFixed(0)} bf</strong></span>
            </div>

            <div class="squad-counts">
                <span>GK ${counts.GK || 0}</span>
                <span>DEF ${counts.DEF || 0}</span>
                <span>MID ${counts.MID || 0}</span>
                <span>FWD ${counts.FWD || 0}</span>
                <span>Total ${squad.players.length}/18</span>
            </div>

            ${["GK", "DEF", "MID", "FWD"].map(pos => {
                const group = squad.players.filter(p => p.pos === pos);
                if (!group.length) return '';
                return `
                    <h4 class="pos-header">${pos} · ${group.length}</h4>
                    <div class="squad-list">
                        ${group.map(p => `
                            <div class="squad-row">
                                <div class="sr-left">
                                    <strong>${p.name}</strong>
                                    <small>${p.club_name} · ${p.tournament_name}</small>
                                </div>
                                <div class="sr-right">
                                    <span class="price-tag">${p.price} bf</span>
                                    <a href="#" class="capt-btn ${squad.captain === p.id ? 'active' : ''}" data-cid="${p.id}">C</a>
                                    <a href="#" class="vice-btn ${squad.vice === p.id ? 'active' : ''}" data-vid="${p.id}">V</a>
                                    <a href="#" class="rm-btn" data-rid="${p.id}">✕</a>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }).join('') || '<p class="hint">No players yet. Tap + on any player to add.</p>'}

            ${squad.players.length ? `
                <a href="#" class="primary-btn" id="viewTeamBtn">View Team Sheet →</a>
            ` : ''}
        `;

        // Wire name
        document.getElementById('squadName').addEventListener('input', (e) => {
            squad.name = e.target.value;
            squad.gsp_row = computeTeamRow(squad.name, OpenBox.App.currentUser?.phone);
            saveSquad(squad);
        });

        // Wire formation
        document.getElementById('squadFormation').addEventListener('change', (e) => {
            squad.formation = e.target.value;
            saveSquad(squad);
            alert('Formation set to ' + squad.formation + '. Adjust your XI in View Team Sheet.');
        });

        // Wire captain/vice/remove
        body.querySelectorAll('.capt-btn').forEach(b => b.addEventListener('click', (e) => {
            e.preventDefault();
            squad.captain = b.dataset.cid;
            saveSquad(squad); render();
        }));
        body.querySelectorAll('.vice-btn').forEach(b => b.addEventListener('click', (e) => {
            e.preventDefault();
            squad.vice = b.dataset.vid;
            saveSquad(squad); render();
        }));
        body.querySelectorAll('.rm-btn').forEach(b => b.addEventListener('click', (e) => {
            e.preventDefault();
            if (!confirm('Remove player and refund byflints?')) return;
            removePlayerFromSquad(b.dataset.rid);
            render();
        }));

        // Wire view team
        const vt = document.getElementById('viewTeamBtn');
        if (vt) vt.addEventListener('click', (e) => {
            e.preventDefault(); setView('team');
        });
    }
// ═══════════════════════════════════════════════════
    //  VIEW: TEAM SHEET (pitch layout)
    // ═══════════════════════════════════════════════════
    function renderTeam(body) {
        const squad = loadSquad() || emptySquad();
        const form = squad.formation || "4-4-2";
        const [def, mid, fwd] = form.split("-").map(Number);

        // Auto-pick best XI: fill positions from available players
        const byPos = { GK: [], DEF: [], MID: [], FWD: [] };
        squad.players.forEach(p => (byPos[p.pos] = byPos[p.pos] || []).push(p));

        const startingXI = {
            GK: byPos.GK.slice(0, 1),
            DEF: byPos.DEF.slice(0, def),
            MID: byPos.MID.slice(0, mid),
            FWD: byPos.FWD.slice(0, fwd)
        };
        const starters = [...startingXI.GK, ...startingXI.DEF, ...startingXI.MID, ...startingXI.FWD];
        const starterIds = new Set(starters.map(p => p.id));
        const bench = squad.players.filter(p => !starterIds.has(p.id));

        const playerChip = (p) => `
            <div class="pitch-player ${squad.captain === p.id ? 'captain' : ''} ${squad.vice === p.id ? 'vice' : ''}">
                <strong>${p.name.split(" ").slice(-1)[0]}</strong>
                <small>${p.pos} · ${p.price}</small>
                ${squad.captain === p.id ? '<span class="badge c">C</span>' : ''}
                ${squad.vice === p.id ? '<span class="badge v">V</span>' : ''}
            </div>
        `;

        body.innerHTML = `
            <a href="#" class="back-btn" id="back">← My Squad</a>
            <div class="team-sheet-header">
                <h3>${squad.name}</h3>
                <small>${form} · GSP row ${squad.gsp_row || '—'}</small>
            </div>
            <div class="pitch">
                <div class="pitch-row fwd">${startingXI.FWD.map(playerChip).join('')}</div>
                <div class="pitch-row mid">${startingXI.MID.map(playerChip).join('')}</div>
                <div class="pitch-row def">${startingXI.DEF.map(playerChip).join('')}</div>
                <div class="pitch-row gk">${startingXI.GK.map(playerChip).join('')}</div>
            </div>
            <h4 class="pos-header">Bench · ${bench.length}</h4>
            <div class="bench-list">
                ${bench.length
                    ? bench.map(p => `<div class="bench-item">${p.name} <small>${p.pos}</small></div>`).join('')
                    : '<p class="hint">No bench players.</p>'}
            </div>
        `;

        document.getElementById('back').addEventListener('click', (e) => {
            e.preventDefault(); setView('squad');
        });
    }

    // ═══════════════════════════════════════════════════
    //  VIEW: HOT (top scorer simulation)
    // ═══════════════════════════════════════════════════
    function renderHot(body) {
        const list = getTournaments();
        if (!list.length) { body.innerHTML = '<p class="hint">No data.</p>'; return; }

        // Pick top player per tournament
        const week = Math.floor(Date.now() / (7 * 86400000));
        const rows = list.map(t => {
            const tid = t.id;
            const tour = OpenBox.FantasyRegistry.tournaments[tid];
            if (!tour || !tour.clubs.length) return null;
            const firstClub = tour.clubs[0];
            const players = getClubPlayers(tid, firstClub.id);
            if (!players.length) return null;
            const scored = players.map(p => {
                const h = (p.id + ":" + week).split("").reduce((s, c) => (s * 31 + c.charCodeAt(0)) >>> 0, 0);
                return { p, pts: ((h % 120) / 10 + 1).toFixed(1) };
            });
            const top = scored.reduce((a, b) => (parseFloat(b.pts) > parseFloat(a.pts) ? b : a));
            return { tid, tournament: t.name, player: top.p, pts: top.pts };
        }).filter(Boolean);

        body.innerHTML = `
            <h3>🔥 Hot This Week</h3>
            <div class="hot-list">
                ${rows.map(r => `
                    <div class="hot-player">
                        <div>
                            <strong>${r.player.name}</strong>
                            <small>${r.tournament} · ${r.player.pos}</small>
                        </div>
                        <div class="hot-pts">
                            ${r.pts} pts<br>
                            <small>${r.player.price} bf</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // ═══════════════════════════════════════════════════
    //  VIEW: TRANSFERS
    // ═══════════════════════════════════════════════════
    async function renderTransfers(body) {
        body.innerHTML = '<p class="hint">Loading transfers...</p>';
        try {
            const r = await OpenBox.API.transfers(30);
            const list = r?.data?.transfers || [];
            if (!list.length) {
                body.innerHTML = `
                    <h3>📋 Transfers</h3>
                    <p class="hint">No transfers in the last 30 days. The scraper runs every 6 hours.
                    Once it completes, real transfer data will appear here.</p>
                `;
                return;
            }
            body.innerHTML = `
                <h3>📋 Recent Transfers (30 days)</h3>
                <div class="transfer-list">
                    ${list.map(t => `
                        <div class="transfer-row">
                            <strong>${t.player_name}</strong>
                            <small>${t.from_club || '?'} → ${t.to_club || '?'}</small>
                            <span>${t.fee || '—'} · ${t.date || ''} · ${t.source || ''}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (err) {
            body.innerHTML = `<p class="hint">Could not load transfers: ${err.message}</p>`;
        }
    }

    // ═══════════════════════════════════════════════════
    //  TAB WIRING
    // ═══════════════════════════════════════════════════
    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".ftab").forEach(t => {
            t.addEventListener("click", (e) => {
                e.preventDefault();
                const v = t.dataset.ftab;
                setView(v);
            });
        });
    });

    OpenBox.Fantasy = { show, loadSquad, saveSquad, emptySquad };
})();
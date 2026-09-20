/**
 * Fantasy workspace.
 * Player source order:
 *   1. Backend /api/fantasy/clubs/{tid}:{cid}/players  (DB, live)
 *   2. Local OpenBox.FantasyRegistry                    (registry fallback)
 *   3. Graceful empty state                             (never crashes)
 */
(function () {

    const SQUAD_KEY = "openbox_squad";
    const _playerCache = {};       // tid:cid -> array
    const _cachePromise = {};      // tid:cid -> Promise

    /* ─── Squad storage ─── */
    function loadSquad() {
        const phone = OpenBox.App?.currentUser?.phone;
        if (!phone) return null;
        const all = JSON.parse(localStorage.getItem(SQUAD_KEY) || "{}");
        return all[phone] || null;
    }
    function saveSquad(squad) {
        const phone = OpenBox.App?.currentUser?.phone;
        if (!phone) return;
        const all = JSON.parse(localStorage.getItem(SQUAD_KEY) || "{}");
        all[phone] = squad;
        localStorage.setItem(SQUAD_KEY, JSON.stringify(all));
    }
    function emptySquad() {
        return {
            name: (OpenBox.App?.currentUser?.fullName || "My") + "'s XI",
            country: OpenBox.App?.currentUser?.country || "NG",
            formation: "4-4-2",
            players: [],
            captain: null,
            vice: null,
            gsp_row: null,
            created_at: new Date().toISOString()
        };
    }

    /* ─── Tournament access ─── */
    function getTournaments() {
        const reg = window.OpenBox?.FantasyRegistry?.tournaments;
        if (!reg || typeof reg !== "object") return [];
        return Object.keys(reg).map(function (k) {
            const t = reg[k] || {};
            const clubs = Array.isArray(t.clubs) ? t.clubs : [];
            return {
                id: k,
                name: t.name || k.toUpperCase(),
                region: t.region || "Other",
                type: t.type || "domestic",
                club_count: clubs.length
            };
        });
    }

    function getTournament(id) {
        const t = OpenBox.FantasyRegistry?.tournaments?.[id];
        if (!t) return null;
        const clubs = Array.isArray(t.clubs) ? t.clubs : [];
        return {
            ...t,
            clubs: clubs.map(function (c, i) {
                return { id: c.id, name: c.name || c.id, col: i };
            })
        };
    }

    function getClubName(tid, cid) {
        const t = OpenBox.FantasyRegistry?.tournaments?.[tid];
        if (!t) return cid;
        const c = (t.clubs || []).find(function (x) { return x.id === cid; });
        return (c && c.name) || cid;
    }

    /* ─── PRICE + POINT helpers ─── */
    const TIER_BASE = {
        npfl:120, egypt_pl:140, sa_psl:140, botola:140,
        cafcl:250, cafcc:250,
        brasileirao_b:280, brasileirao_a:350, argentina_primera:350,
        mls:400, ligamx:400, j1:400, saudi_pl:450,
        eredivisie:400, portugal:450, turkey:400,
        epl:600, laliga:600, seriea:600, bundes:550, ligue1:500,
        ucl:800, uel:700, uecl:600,
        libertadores:500, sudamericana:450, concacaf_cl:450, afc_cl:500,
        worldcup:1000, afcon:800, euro:900, copa_america:800
    };
    const POS_BONUS = { GK:0, DEF:20, MID:40, FWD:80 };

    function priceFor(tid, name, pos) {
        const base = TIER_BASE[tid] || 300;
        const hash = (name || "").split("").reduce(function (s, c) { return s + c.charCodeAt(0); }, 0);
        return base + (POS_BONUS[pos] || 40) + (hash % 60);
    }

    /* ─── Normalize position strings ─── */
    function normPos(p) {
        const s = (p || "").toString().toLowerCase();
        if (s.startsWith("g") || s === "gk" || s === "goalkeeper") return "GK";
        if (s.startsWith("d") || s === "def" || s === "defender") return "DEF";
        if (s.startsWith("m") || s === "mid" || s === "midfielder") return "MID";
        if (s.startsWith("f") || s.startsWith("a") || s === "forward" || s === "attacker") return "FWD";
        return "MID";
    }

    /* ─── Backend fetch (with cache) ─── */
    function fetchFromBackend(tid, cid) {
        const key = tid + ":" + cid;
        if (_cachePromise[key]) return _cachePromise[key];

        _cachePromise[key] = (async function () {
            try {
                const url = "/api/fantasy/clubs/" + encodeURIComponent(key) + "/players";
                const r = await fetch(url, { credentials: "include" });
                if (!r.ok) throw new Error("HTTP " + r.status);
                const data = await r.json();
                const clubName = getClubName(tid, cid);
                const tName = OpenBox.FantasyRegistry?.tournaments?.[tid]?.name || tid;
                const list = (data.players || []).map(function (p) {
                    return {
                        id: p.id,
                        name: p.name || "Unknown",
                        pos: normPos(p.position),
                        price: p.price || priceFor(tid, p.name, normPos(p.position)),
                        points: p.points_this_week || 0,
                        number: p.number,
                        nationality: p.nationality,
                        club_id: cid,
                        club_name: clubName,
                        tournament_id: tid,
                        tournament_name: tName,
                        source: "db"
                    };
                });
                _playerCache[key] = list;
                return list;
            } catch (e) {
                // Swallow — fall back to local
                return null;
            }
        })();

        return _cachePromise[key];
    }

    /* ─── Local registry fallback ─── */
    function getLocalPlayers(tid, cid) {
        const t = OpenBox.FantasyRegistry?.tournaments?.[tid];
        if (!t) return [];
        const clubs = Array.isArray(t.clubs) ? t.clubs : [];
        const club = clubs.find(function (c) { return c.id === cid; });
        if (!club) return [];
        const raw = Array.isArray(club.players) ? club.players : [];
        return raw.map(function (p, i) {
            const pos = normPos(p.pos);
            return {
                id: tid + ":" + cid + ":" + i,
                name: p.name || ("Player " + (i + 1)),
                pos: pos,
                price: priceFor(tid, p.name, pos),
                points: 0,
                club_id: cid,
                club_name: club.name || cid,
                tournament_id: tid,
                tournament_name: t.name || tid,
                source: "registry"
            };
        });
    }

    /* ─── Public player fetch: async ─── */
    async function getClubPlayers(tid, cid) {
        const key = tid + ":" + cid;
        if (_playerCache[key]) return _playerCache[key];

        const fromDb = await fetchFromBackend(tid, cid);
        if (fromDb && fromDb.length) return fromDb;

        const local = getLocalPlayers(tid, cid);
        _playerCache[key] = local;
        return local;
    }

    /* ─── GSP row anchor ─── */
    function computeTeamRow(teamName, phone) {
        const L = String(teamName || "").replace(/[^a-z]/gi, "").length;
        const S = String(phone || "").split("").filter(function (ch) { return /\d/.test(ch); })
            .reduce(function (s, ch) { return s + parseInt(ch, 10); }, 0);
        return ((L + S - 1) % 64) + 1;
    }

    /* ─── View state ─── */
    let currentView = "tournaments";

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
        document.querySelectorAll(".ftab").forEach(function (t) {
            t.classList.toggle("active", t.dataset.ftab === v);
        });
        render();
    }

    /* ─── Tournaments ─── */
    function renderTournaments(body) {
        const list = getTournaments();
        if (!list.length) {
            body.innerHTML = '<p class="hint">No tournaments loaded. Check that fantasy_registry*.js files are loaded in index.html.</p>';
            return;
        }

        const byRegion = {};
        list.forEach(function (t) {
            const r = t.region || "Other";
            if (!byRegion[r]) byRegion[r] = [];
            byRegion[r].push(t);
        });

        let html = "";
        Object.keys(byRegion).forEach(function (region) {
            html += '<h3 class="region-header">' + escapeHtml(region) + '</h3>';
            html += '<div class="tournament-list">';
            html += byRegion[region].map(function (t) {
                return '<a href="#" class="tournament-item" data-tid="' + t.id + '">' +
                    '<div><strong>' + escapeHtml(t.name) + '</strong>' +
                    '<small>' + t.club_count + ' clubs · ' + escapeHtml(t.type) + '</small></div>' +
                    '<span class="chev">›</span></a>';
            }).join("");
            html += '</div>';
        });
        body.innerHTML = html;

        body.querySelectorAll(".tournament-item").forEach(function (el) {
            el.addEventListener("click", function (e) {
                e.preventDefault();
                renderClubs(body, el.dataset.tid);
            });
        });
    }

    function renderClubs(body, tid) {
        const t = getTournament(tid);
        if (!t) { body.innerHTML = '<p class="hint">Tournament not found.</p>'; return; }

        body.innerHTML =
            '<a href="#" class="back-btn" id="back">← Tournaments</a>' +
            '<h3>' + escapeHtml(t.name) + '</h3>' +
            '<small class="hint">' + t.clubs.length + ' clubs</small>' +
            '<div class="club-grid">' +
                t.clubs.map(function (c) {
                    return '<a href="#" class="club-chip" data-cid="' + c.id + '">' +
                        '<span>' + escapeHtml(c.name) + '</span>' +
                        '<small>col ' + c.col + '</small></a>';
                }).join("") +
            '</div>';

        document.getElementById("back").addEventListener("click", function (e) {
            e.preventDefault(); setView("tournaments");
        });
        body.querySelectorAll(".club-chip").forEach(function (el) {
            el.addEventListener("click", function (e) {
                e.preventDefault();
                renderPlayers(body, tid, el.dataset.cid);
            });
        });
    }

    async function renderPlayers(body, tid, cid) {
        const t = getTournament(tid);
        const club = t ? t.clubs.find(function (c) { return c.id === cid; }) : null;
        if (!club) { body.innerHTML = '<p class="hint">Club not found.</p>'; return; }

        // Loading state
        body.innerHTML =
            '<a href="#" class="back-btn" id="back">← ' + escapeHtml(t.name) + '</a>' +
            '<h3>' + escapeHtml(club.name) + '</h3>' +
            '<p class="hint">Loading squad...</p>';
        document.getElementById("back").addEventListener("click", function (e) {
            e.preventDefault(); renderClubs(body, tid);
        });

        const players = await getClubPlayers(tid, cid);
        const squad = loadSquad() || emptySquad();
        const owned = new Set(squad.players.map(function (p) { return p.id; }));
        const balance = OpenBox.App?.currentUser?.byflints || 0;

        if (!players.length) {
            body.innerHTML =
                '<a href="#" class="back-btn" id="back">← ' + escapeHtml(t.name) + '</a>' +
                '<h3>' + escapeHtml(club.name) + '</h3>' +
                '<p class="hint">No players found for this club yet. ' +
                'Run the scraper from <code>/admin.html</code> to populate this club.</p>';
            document.getElementById("back").addEventListener("click", function (e) {
                e.preventDefault(); renderClubs(body, tid);
            });
            return;
        }

        const sourceBadge = players[0].source === "db"
            ? '<span class="src-badge db">LIVE</span>'
            : '<span class="src-badge local">REGISTRY</span>';

        body.innerHTML =
            '<a href="#" class="back-btn" id="back">← ' + escapeHtml(t.name) + '</a>' +
            '<h3>' + escapeHtml(club.name) + sourceBadge + '</h3>' +
            '<div class="balance-line"><span>Balance: <strong>' + Number(balance).toFixed(0) + ' bf</strong></span>' +
            '<span>' + squad.players.length + ' in squad · ' + players.length + ' available</span></div>' +
            '<div class="player-list">' +
                players.map(function (p) {
                    const isOwned = owned.has(p.id);
                    const canAfford = balance >= p.price;
                    return '<div class="player-card">' +
                        '<div class="pc-left"><strong>' + escapeHtml(p.name) + '</strong>' +
                        '<small>' + p.pos + ' · ' + p.price + ' bf' +
                        (p.points ? ' · ' + p.points + ' pts' : '') + '</small></div>' +
                        '<div class="pc-right">' +
                        (isOwned
                            ? '<span class="owned-tag">✓ Owned</span>'
                            : '<a href="#" class="add-btn ' + (canAfford ? '' : 'disabled') + '" ' +
                              'data-pid="' + escapeHtml(p.id) + '" data-name="' + escapeHtml(p.name) + '" ' +
                              'data-pos="' + p.pos + '" data-price="' + p.price + '" ' +
                              'data-tid="' + tid + '" data-cid="' + cid + '" ' +
                              'data-tname="' + escapeHtml(t.name) + '" data-cname="' + escapeHtml(club.name) + '">' +
                              '+ ' + p.price + '</a>') +
                        '</div></div>';
                }).join("") +
            '</div>';

        document.getElementById("back").addEventListener("click", function (e) {
            e.preventDefault(); renderClubs(body, tid);
        });
        body.querySelectorAll(".add-btn").forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                if (btn.classList.contains("disabled")) return alert("Not enough byflints.");
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

    /* ─── Squad ops ─── */
    function addPlayerToSquad(player) {
        const squad = loadSquad() || emptySquad();
        if (squad.players.find(function (p) { return p.id === player.id; })) return alert("Already in your squad.");
        if (squad.players.length >= 18) return alert("Squad full (18 players max). Remove one first.");
        const sameClub = squad.players.filter(function (p) { return p.club_id === player.club_id; }).length;
        if (sameClub >= 3) return alert("Max 3 players from " + player.club_name + ".");
        const balance = OpenBox.App?.currentUser?.byflints || 0;
        if (balance < player.price) return alert("Not enough byflints.");

        OpenBox.App.currentUser.byflints = balance - player.price;
        squad.players.push(player);
        if (squad.gsp_row === null) squad.gsp_row = computeTeamRow(squad.name, OpenBox.App.currentUser?.phone);
        saveSquad(squad);
        updateBalanceUI();
        alert(player.name + " added for " + player.price + " bf.");
    }

    function removePlayerFromSquad(playerId) {
        const squad = loadSquad();
        if (!squad) return;
        const idx = squad.players.findIndex(function (p) { return p.id === playerId; });
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
        const el = document.getElementById("walletBalanceDisplay");
        if (el) el.textContent = Number(OpenBox.App?.currentUser?.byflints || 0).toFixed(2);
    }


    /* ─── Squad view ─── */
    function renderSquad(body) {
        const squad = loadSquad() || emptySquad();
        const FORMS = ["4-4-2","4-3-3","3-5-2","3-4-3","5-3-2","5-4-1"];
        const counts = { GK: 0, DEF: 0, MID: 0, FWD: 0 };
        squad.players.forEach(function (p) { counts[p.pos] = (counts[p.pos] || 0) + 1; });

        body.innerHTML =
            '<div class="squad-header">' +
                '<input type="text" id="squadName" value="' + escapeHtml(squad.name) + '" maxlength="40">' +
                '<select id="squadFormation">' +
                    FORMS.map(function (f) {
                        return '<option ' + (f === squad.formation ? "selected" : "") + '>' + f + '</option>';
                    }).join("") +
                '</select>' +
            '</div>' +
            '<div class="squad-meta">' +
                '<span>Country: <strong>' + escapeHtml(squad.country) + '</strong></span>' +
                '<span>GSP row: <strong>' + (squad.gsp_row || "—") + '</strong></span>' +
                '<span>Balance: <strong>' + Number(OpenBox.App?.currentUser?.byflints || 0).toFixed(0) + ' bf</strong></span>' +
            '</div>' +
            '<div class="squad-counts">' +
                '<span>GK ' + counts.GK + '</span>' +
                '<span>DEF ' + counts.DEF + '</span>' +
                '<span>MID ' + counts.MID + '</span>' +
                '<span>FWD ' + counts.FWD + '</span>' +
                '<span>Total ' + squad.players.length + '/18</span>' +
            '</div>' +
            (["GK","DEF","MID","FWD"].map(function (pos) {
                const group = squad.players.filter(function (p) { return p.pos === pos; });
                if (!group.length) return "";
                return '<h4 class="pos-header">' + pos + ' · ' + group.length + '</h4>' +
                    '<div class="squad-list">' +
                        group.map(function (p) {
                            return '<div class="squad-row">' +
                                '<div class="sr-left"><strong>' + escapeHtml(p.name) + '</strong>' +
                                '<small>' + escapeHtml(p.club_name) + ' · ' + escapeHtml(p.tournament_name) + '</small></div>' +
                                '<div class="sr-right">' +
                                    '<span class="price-tag">' + p.price + ' bf</span>' +
                                    '<a href="#" class="capt-btn ' + (squad.captain === p.id ? "active" : "") + '" data-cid="' + p.id + '">C</a>' +
                                    '<a href="#" class="vice-btn ' + (squad.vice === p.id ? "active" : "") + '" data-vid="' + p.id + '">V</a>' +
                                    '<a href="#" class="rm-btn" data-rid="' + p.id + '">✕</a>' +
                                '</div></div>';
                        }).join("") +
                    '</div>';
            }).join("") || '<p class="hint">No players yet. Tap + on any player to add.</p>') +
            (squad.players.length ? '<a href="#" class="primary-btn" id="viewTeamBtn">View Team Sheet →</a>' : '');

        const nameInput = document.getElementById("squadName");
        if (nameInput) nameInput.addEventListener("input", function (e) {
            squad.name = e.target.value;
            squad.gsp_row = computeTeamRow(squad.name, OpenBox.App.currentUser?.phone);
            saveSquad(squad);
        });
        const formSel = document.getElementById("squadFormation");
        if (formSel) formSel.addEventListener("change", function (e) {
            squad.formation = e.target.value;
            saveSquad(squad);
            alert("Formation set to " + squad.formation);
        });
        body.querySelectorAll(".capt-btn").forEach(function (b) {
            b.addEventListener("click", function (e) {
                e.preventDefault(); squad.captain = b.dataset.cid; saveSquad(squad); render();
            });
        });
        body.querySelectorAll(".vice-btn").forEach(function (b) {
            b.addEventListener("click", function (e) {
                e.preventDefault(); squad.vice = b.dataset.vid; saveSquad(squad); render();
            });
        });
        body.querySelectorAll(".rm-btn").forEach(function (b) {
            b.addEventListener("click", function (e) {
                e.preventDefault();
                if (!confirm("Remove player and refund byflints?")) return;
                removePlayerFromSquad(b.dataset.rid);
                render();
            });
        });
        const vt = document.getElementById("viewTeamBtn");
        if (vt) vt.addEventListener("click", function (e) {
            e.preventDefault(); setView("team");
        });
    }

    /* ─── Team sheet ─── */
    function renderTeam(body) {
        const squad = loadSquad() || emptySquad();
        const form = squad.formation || "4-4-2";
        const parts = form.split("-").map(Number);
        const def = parts[0] || 4, mid = parts[1] || 4, fwd = parts[2] || 2;

        const byPos = { GK: [], DEF: [], MID: [], FWD: [] };
        squad.players.forEach(function (p) {
            if (!byPos[p.pos]) byPos[p.pos] = [];
            byPos[p.pos].push(p);
        });

        const startingXI = {
            GK: byPos.GK.slice(0, 1),
            DEF: byPos.DEF.slice(0, def),
            MID: byPos.MID.slice(0, mid),
            FWD: byPos.FWD.slice(0, fwd)
        };
        const starters = [].concat(startingXI.GK, startingXI.DEF, startingXI.MID, startingXI.FWD);
        const starterIds = new Set(starters.map(function (p) { return p.id; }));
        const bench = squad.players.filter(function (p) { return !starterIds.has(p.id); });

        function chip(p) {
            return '<div class="pitch-player ' +
                (squad.captain === p.id ? "captain" : "") + ' ' +
                (squad.vice === p.id ? "vice" : "") + '">' +
                '<strong>' + escapeHtml(p.name.split(" ").slice(-1)[0]) + '</strong>' +
                '<small>' + p.pos + ' · ' + p.price + '</small>' +
                (squad.captain === p.id ? '<span class="badge c">C</span>' : '') +
                (squad.vice === p.id ? '<span class="badge v">V</span>' : '') +
                '</div>';
        }

        body.innerHTML =
            '<a href="#" class="back-btn" id="back">← My Squad</a>' +
            '<div class="team-sheet-header"><h3>' + escapeHtml(squad.name) + '</h3>' +
            '<small>' + form + ' · GSP row ' + (squad.gsp_row || "—") + '</small></div>' +
            '<div class="pitch">' +
                '<div class="pitch-row fwd">' + startingXI.FWD.map(chip).join("") + '</div>' +
                '<div class="pitch-row mid">' + startingXI.MID.map(chip).join("") + '</div>' +
                '<div class="pitch-row def">' + startingXI.DEF.map(chip).join("") + '</div>' +
                '<div class="pitch-row gk">' + startingXI.GK.map(chip).join("") + '</div>' +
            '</div>' +
            '<h4 class="pos-header">Bench · ' + bench.length + '</h4>' +
            '<div class="bench-list">' +
                (bench.length
                    ? bench.map(function (p) {
                        return '<div class="bench-item">' + escapeHtml(p.name) + ' <small>' + p.pos + '</small></div>';
                    }).join("")
                    : '<p class="hint">No bench players.</p>') +
            '</div>';

        document.getElementById("back").addEventListener("click", function (e) {
            e.preventDefault(); setView("squad");
        });
    }

    /* ─── Hot ─── */
    async function renderHot(body) {
        body.innerHTML = '<p class="hint">Loading hot players...</p>';
        const list = getTournaments();
        if (!list.length) { body.innerHTML = '<p class="hint">No data.</p>'; return; }

        const week = Math.floor(Date.now() / (7 * 86400000));
        const rows = [];
        for (const t of list) {
            const tour = OpenBox.FantasyRegistry.tournaments[t.id];
            if (!tour || !Array.isArray(tour.clubs) || !tour.clubs.length) continue;
            const firstClub = tour.clubs[0];
            try {
                const players = await getClubPlayers(t.id, firstClub.id);
                if (!players.length) continue;
                const scored = players.map(function (p) {
                    if (p.points) return { p: p, pts: Number(p.points) };
                    const h = (p.id + ":" + week).split("").reduce(function (s, c) { return (s * 31 + c.charCodeAt(0)) >>> 0; }, 0);
                    return { p: p, pts: (h % 120) / 10 + 1 };
                });
                const top = scored.reduce(function (a, b) { return b.pts > a.pts ? b : a; });
                rows.push({ tid: t.id, tournament: t.name, player: top.p, pts: top.pts.toFixed(1) });
            } catch (e) { /* skip tournament */ }
        }

        if (!rows.length) {
            body.innerHTML = '<p class="hint">Hot list populates once clubs have players. Run the scraper from /admin.html.</p>';
            return;
        }

        rows.sort(function (a, b) { return parseFloat(b.pts) - parseFloat(a.pts); });

        body.innerHTML =
            '<h3>🔥 Hot This Week</h3><div class="hot-list">' +
            rows.slice(0, 20).map(function (r) {
                return '<div class="hot-player">' +
                    '<div><strong>' + escapeHtml(r.player.name) + '</strong>' +
                    '<small>' + escapeHtml(r.tournament) + ' · ' + r.player.pos + '</small></div>' +
                    '<div class="hot-pts">' + r.pts + ' pts<br><small>' + r.player.price + ' bf</small></div>' +
                    '</div>';
            }).join("") + '</div>';
    }



    /* ─── Transfers ─── */
    async function renderTransfers(body) {
    body.innerHTML =
        '<h3>📋 Live Transfers</h3>' +
        '<div class="transfer-regions">' +
            '<button class="region-btn active" data-region="world">🌍 All</button>' +
            '<button class="region-btn" data-region="europe">🇪🇺 Europe</button>' +
            '<button class="region-btn" data-region="africa">🌍 Africa</button>' +
            '<button class="region-btn" data-region="americas">🌎 Americas</button>' +
            '<button class="region-btn" data-region="asia">🌏 Asia</button>' +
        '</div>' +
        '<div id="transferListBox"><p class="hint">Loading transfers...</p></div>';

    body.querySelectorAll(".region-btn").forEach(function (b) {
        b.addEventListener("click", function (e) {
            e.preventDefault();
            body.querySelectorAll(".region-btn").forEach(function (x) { x.classList.remove("active"); });
            b.classList.add("active");
            loadRegionTransfers(b.dataset.region);
        });
    });

    loadRegionTransfers("world");
}

async function loadRegionTransfers(region) {
    const box = document.getElementById("transferListBox");
    if (!box) return;
    box.innerHTML = '<p class="hint">Loading ' + region + ' transfers...</p>';

    try {
        const r = await fetch("/api/transfers/live?region=" + region + "&limit=30", { credentials: "include" });
        const data = await r.json();
        const items = data.transfers || [];

        if (!items.length) {
            box.innerHTML = '<p class="hint">No transfers found' +
                (data.note ? ' — ' + escapeHtml(data.note) : '') + '.</p>';
            return;
        }

        const srcBadge = data.source === "gnews"
            ? '<span class="src-badge db">LIVE</span>'
            : (data.source === "gnews-cache" ? '<span class="src-badge db">LIVE</span>'
              : '<span class="src-badge local">CACHED</span>');

        box.innerHTML =
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">' +
                '<small class="hint">' + items.length + ' stories' + srcBadge + '</small>' +
            '</div>' +
            '<div class="transfer-list">' +
            items.map(function (t) {
                const headline = t.title || (t.player_name +
                    (t.to_club ? ' → ' + t.to_club : ''));
                const meta = [];
                if (t.from_club && t.to_club) meta.push(t.from_club + ' → ' + t.to_club);
                if (t.fee) meta.push(t.fee);
                if (t.date) meta.push(t.date);
                if (t.source) meta.push(t.source);
                return '<a class="transfer-row" href="' + escapeHtml(t.url || "#") +
                    '" target="_blank" rel="noopener">' +
                    (t.image ? '<div class="news-img" style="background-image:url(' + escapeHtml(t.image) + ')"></div>' : '') +
                    '<div style="flex:1;min-width:0;">' +
                        '<strong class="transfer-title">' + escapeHtml(headline) + '</strong>' +
                        (meta.length ? '<small>' + escapeHtml(meta.join(' · ')) + '</small>' : '') +
                        (t.description ? '<p class="news-desc">' + escapeHtml(t.description) + '</p>' : '') +
                    '</div>' +
                '</a>';
            }).join("") +
            '</div>';
    } catch (e) {
        box.innerHTML = '<p class="hint">Error: ' + escapeHtml(e.message) + '</p>';
    }
}

    /* ─── Tab wiring ─── */
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".ftab").forEach(function (t) {
            t.addEventListener("click", function (e) {
                e.preventDefault();
                setView(t.dataset.ftab);
            });
        });
    });
OpenBox.Fantasy = {
    show: show,
    loadSquad: loadSquad,
    saveSquad: saveSquad,
    emptySquad: emptySquad,
    loadRegionTransfers: loadRegionTransfers,
    clearPlayerCache: function () {
        Object.keys(_playerCache).forEach(function (k) { delete _playerCache[k]; });
        Object.keys(_cachePromise).forEach(function (k) { delete _cachePromise[k]; });
    }
};
    
})();
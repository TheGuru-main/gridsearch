(function () {
    const COUNTRY_INFO = {
        NG: { dial: '234', len: 10, dialDisplay: '+234' },
        GH: { dial: '233', len: 9,  dialDisplay: '+233' },
        US: { dial: '1',   len: 10, dialDisplay: '+1' },
        IN: { dial: '91',  len: 10, dialDisplay: '+91' },
        GB: { dial: '44',  len: 10, dialDisplay: '+44' }
    };

    // ═══════════════════════════════════════════════
    //  ON-SCREEN DEBUG PANEL (phone-friendly)
    // ═══════════════════════════════════════════════
    function showDebug(msg, isError) {
        let panel = document.getElementById('__debugPanel');
        if (!panel) {
            panel = document.createElement('div');
            panel.id = '__debugPanel';
            panel.style.cssText = `
                position: fixed; top: 0; left: 0; right: 0;
                max-height: 45vh; overflow-y: auto;
                background: rgba(0,0,0,0.92); color: #0f0;
                font-family: monospace; font-size: 11px;
                padding: 8px; z-index: 999999;
                border-bottom: 2px solid #0f0;
                white-space: pre-wrap; word-break: break-word;
            `;
            const closeBtn = document.createElement('div');
            closeBtn.textContent = '✕ close debug';
            closeBtn.style.cssText = 'text-align:right;color:#f66;font-weight:bold;margin-bottom:6px;cursor:pointer;';
            closeBtn.onclick = () => panel.style.display = 'none';
            panel.appendChild(closeBtn);

            const logBox = document.createElement('div');
            logBox.id = '__debugLog';
            panel.appendChild(logBox);

            document.body.appendChild(panel);
        }
        panel.style.display = 'block';
        const log = document.getElementById('__debugLog');
        const line = document.createElement('div');
        line.style.color = isError ? '#f66' : '#0f0';
        line.textContent = (isError ? '✘ ' : '✔ ') + msg;
        log.appendChild(line);
    }

    window.showDebug = showDebug;

    // ═══════════════════════════════════════════════
    //  SHOW WHAT LOADED
    // ═══════════════════════════════════════════════
    window.addEventListener('DOMContentLoaded', () => {
        showDebug('DOM ready');
        showDebug('OpenBox: ' + (typeof OpenBox));
        showDebug('OpenBox.API: ' + (typeof OpenBox?.API));
        showDebug('OpenBox.API.signup: ' + (typeof OpenBox?.API?.signup));
        showDebug('OpenBox.App: ' + (typeof OpenBox?.App));
        showDebug('OpenBox.App.afterLogin: ' + (typeof OpenBox?.App?.afterLogin));

        const sel = document.getElementById('signupCountry');
        const dial = document.getElementById('signupDial');
        if (sel && dial) {
            sel.addEventListener('change', () => {
                const info = COUNTRY_INFO[sel.value];
                dial.value = info ? info.dialDisplay : '';
                showDebug('country=' + sel.value + ' dial=' + dial.value);
            });
        }

        // Auto-wire the button no matter what
        const btn = document.getElementById('btnSignup');
        if (btn) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                showDebug('btnSignup clicked → calling signup()');
                signup();
            });
            showDebug('btnSignup wired');
        } else {
            showDebug('btnSignup NOT FOUND', true);
        }

        const btnLogin = document.getElementById('btnLogin');
        if (btnLogin) {
            btnLogin.addEventListener('click', (e) => {
                e.preventDefault();
                showDebug('btnLogin clicked → calling login()');
                login();
            });
        }
    });

    // ═══════════════════════════════════════════════
    //  SIGNUP
    // ═══════════════════════════════════════════════
    async function signup() {
        try {
            const name = document.getElementById('signupName').value.trim();
            const phone = document.getElementById('signupPhone').value.trim();
            const email = document.getElementById('signupEmail').value.trim();
            const password = document.getElementById('signupPassword').value;
            const dob = document.getElementById('signupDob').value;
            const talent = document.getElementById('signupTalent').value;
            const country = document.getElementById('signupCountry').value;
            const rulesAccepted = document.getElementById('communityRules').checked;

            showDebug('name=' + name + ' phone=' + phone + ' country=' + country);

            if (!name || !phone || !email || !password || !dob || !talent || !country) {
                showDebug('MISSING FIELD', true);
                return alert('All fields required');
            }
            if (!rulesAccepted) {
                showDebug('RULES NOT ACCEPTED', true);
                return alert('You must accept the Community Rules');
            }

            const info = COUNTRY_INFO[country];
            if (!info) { showDebug('invalid country', true); return alert('Invalid country'); }
            if (phone.startsWith('0')) { showDebug('phone starts with 0', true); return alert('Phone must not start with 0'); }
            if (phone.length !== info.len) {
                showDebug(`phone length ${phone.length} != ${info.len}`, true);
                return alert(`Phone must be ${info.len} digits`);
            }
            const fullPhone = info.dial + phone;
            showDebug('fullPhone=' + fullPhone);

            const age = Math.floor((Date.now() - new Date(dob).getTime()) / (1000*60*60*24*365.25));
            showDebug('age=' + age);
            if (age < 16) { showDebug('underage', true); return alert('You must be 16 or older'); }

            if (typeof OpenBox?.API?.signup !== 'function') {
                showDebug('OpenBox.API.signup NOT A FUNCTION', true);
                return alert('API not loaded. Check /js/api.js on the server.');
            }

            showDebug('calling API.signup...');
            const r = await OpenBox.API.signup({
                full_name: name, phone: fullPhone, email,
                password, dob, talent, country
            });

            showDebug('response ok=' + r.ok + ' status=' + r.status);
            showDebug('response data=' + JSON.stringify(r.data).substring(0, 300));

            if (!r.ok) {
                return alert(r.data?.detail || r.data?.error || 'Signup failed');
            }

            OpenBox.App.currentUser = {
                phone: r.data.phone,
                fullName: r.data.full_name,
                byflints: r.data.byflints
            };

            if (typeof OpenBox?.App?.afterLogin === 'function') {
                await OpenBox.App.afterLogin();
            } else {
                showDebug('afterLogin missing, showing home manually');
                document.querySelectorAll('.workspace').forEach(w => w.classList.remove('active'));
                document.getElementById('workspaceHome').classList.add('active');
                document.getElementById('bottomNav').style.display = 'flex';
            }

            showDebug('SIGNUP SUCCESS');
            alert(`Welcome! You received ${r.data.byflints} byflints.`);
        } catch (err) {
            showDebug('EXCEPTION: ' + err.message, true);
            showDebug('stack: ' + (err.stack || '').substring(0, 300), true);
            alert('Signup error: ' + err.message);
        }
    }

    // ═══════════════════════════════════════════════
    //  LOGIN
    // ═══════════════════════════════════════════════
    async function login() {
        try {
            const phone = document.getElementById('loginPhone').value.trim();
            const password = document.getElementById('loginPassword').value;
            if (!phone || !password) { showDebug('login missing fields', true); return alert('All fields required'); }

            if (typeof OpenBox?.API?.login !== 'function') {
                showDebug('OpenBox.API.login NOT A FUNCTION', true);
                return alert('API not loaded.');
            }

            showDebug('calling API.login...');
            const r = await OpenBox.API.login({ phone, password });
            showDebug('login ok=' + r.ok + ' status=' + r.status);

            if (!r.ok) return alert(r.data?.detail || 'Invalid credentials');

            OpenBox.App.currentUser = {
                phone: r.data.phone,
                fullName: r.data.full_name,
                byflints: r.data.byflints
            };
            if (typeof OpenBox?.App?.afterLogin === 'function') {
                await OpenBox.App.afterLogin();
            }
            showDebug('LOGIN SUCCESS');
        } catch (err) {
            showDebug('LOGIN EXCEPTION: ' + err.message, true);
            alert('Login error: ' + err.message);
        }
    }

    async function logout() {
        try { await OpenBox.API.logout(); } catch (_) {}
        OpenBox.App.currentUser = null;
        OpenBox.UI.showWorkspace('authScreen');
    }

    // Global error catcher
    window.addEventListener('error', (e) => {
        showDebug('RUNTIME: ' + e.message + ' @ ' + e.filename + ':' + e.lineno, true);
    });
    window.addEventListener('unhandledrejection', (e) => {
        showDebug('PROMISE: ' + (e.reason?.message || e.reason), true);
    });

    OpenBox.Auth = { signup, login, logout };
})();
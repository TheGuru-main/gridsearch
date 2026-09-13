(function () {
    const COUNTRY_INFO = {
        NG: { dial: '234', len: 10, dialDisplay: '+234' },
        GH: { dial: '233', len: 9,  dialDisplay: '+233' },
        US: { dial: '1',   len: 10, dialDisplay: '+1' },
        IN: { dial: '91',  len: 10, dialDisplay: '+91' },
        GB: { dial: '44',  len: 10, dialDisplay: '+44' }
    };

    async function signup() {
        const name = document.getElementById('signupName').value.trim();
        const phone = document.getElementById('signupPhone').value.trim();
        const email = document.getElementById('signupEmail').value.trim();
        const password = document.getElementById('signupPassword').value;
        const dob = document.getElementById('signupDob').value;
        const talent = document.getElementById('signupTalent').value;
        const country = document.getElementById('signupCountry').value;
        const rulesAccepted = document.getElementById('communityRules').checked;

        if (!name || !phone || !email || !password || !dob || !talent || !country)
            return alert('All fields required');
        if (!rulesAccepted) return alert('You must accept the Community Rules');

        const info = COUNTRY_INFO[country];
        if (!info) return alert('Invalid country');
        if (phone.startsWith('0')) return alert('Phone must not start with 0');
        if (phone.length !== info.len) return alert(`Phone must be ${info.len} digits`);
        const fullPhone = info.dial + phone;

        const age = Math.floor((Date.now() - new Date(dob).getTime()) / (1000*60*60*24*365.25));
        if (age < 16) return alert('You must be 16 or older');

        const r = await OpenBox.API.signup({
            full_name: name, phone: fullPhone, email,
            password, dob, talent, country
        });
        if (!r.ok) return alert(r.data.detail || r.data.error || 'Signup failed');

        OpenBox.App.currentUser = {
            phone: r.data.phone,
            fullName: r.data.full_name,
            byflints: r.data.byflints
        };
        await OpenBox.App.afterLogin();
        alert(`Welcome! You received ${r.data.byflints} byflints.`);
    }

    async function login() {
        const phone = document.getElementById('loginPhone').value.trim();
        const password = document.getElementById('loginPassword').value;
        if (!phone || !password) return alert('All fields required');

        const r = await OpenBox.API.login({ phone, password });
        if (!r.ok) return alert(r.data.detail || 'Invalid credentials');

        OpenBox.App.currentUser = {
            phone: r.data.phone,
            fullName: r.data.full_name,
            byflints: r.data.byflints
        };
        await OpenBox.App.afterLogin();
    }

    async function logout() {
        await OpenBox.API.logout();
        OpenBox.App.currentUser = null;
        OpenBox.UI.showWorkspace('authScreen');
    }

    document.addEventListener('DOMContentLoaded', () => {
        const sel = document.getElementById('signupCountry');
        const dial = document.getElementById('signupDial');
        if (sel && dial) {
            sel.addEventListener('change', () => {
                const info = COUNTRY_INFO[sel.value];
                dial.value = info ? info.dialDisplay : '';
            });
        }
    });

    OpenBox.Auth = { signup, login, logout };
})();
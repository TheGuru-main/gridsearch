/**
 * Backend API client. All requests include credentials (cookie session).
 */
(function () {
    async function req(path, opts = {}) {
        const r = await fetch(path, {
            credentials: 'include',
            ...opts,
            headers: {
                ...(opts.body && !(opts.body instanceof FormData)
                    ? { 'Content-Type': 'application/json' }
                    : {}),
                ...(opts.headers || {})
            }
        });
        const text = await r.text();
        let data;
        try { data = JSON.parse(text); }
        catch { data = { error: text.substring(0, 200) }; }
        return { ok: r.ok, status: r.status, data };
    }

    OpenBox.API = {
        // Auth
        signup: (payload) => req('/api/auth/signup', { method: 'POST', body: JSON.stringify(payload) }),
        login:  (payload) => req('/api/auth/login',  { method: 'POST', body: JSON.stringify(payload) }),
        logout: ()        => req('/api/auth/logout', { method: 'POST' }),
        me:     ()        => req('/api/me'),

        // Wallet
        wallet: () => req('/api/wallet'),

        // OpenBox items
        items:    (category) => req('/api/openbox/items' + (category ? `?category=${category}` : '')),
        itemDetail: (id) => req(`/api/openbox/items/${id}`),
        itemDownload: (id) => req(`/api/openbox/items/${id}/download`, { method: 'POST' }),
        itemUpload: (formData) => req('/api/openbox/upload', { method: 'POST', body: formData }),

        // Fantasy
        tournaments: () => req('/api/fantasy/tournaments'),
        tournament: (tid) => req(`/api/fantasy/tournaments/${tid}`),
        clubPlayers: (cid) => req(`/api/fantasy/clubs/${cid}/players`),
        transfers: (days = 30) => req(`/api/fantasy/transfers?days=${days}`),
        hot: () => req('/api/fantasy/hot'),
        health: () => req('/api/health'),
    };
})();
/**
 * OpenBox.Storage — localStorage helpers.
 * Must be loaded right after config.js, before any module uses it.
 */
window.OpenBox = window.OpenBox || {};
OpenBox.Storage = {
    getItem: function (key, fallback) {
        if (fallback === undefined) fallback = [];
        try {
            var raw = localStorage.getItem(key);
            if (raw === null) return fallback;
            return JSON.parse(raw);
        } catch (e) {
            console.warn('[storage] getItem failed for', key, e);
            return fallback;
        }
    },
    setItem: function (key, value) {
        try { localStorage.setItem(key, JSON.stringify(value)); }
        catch (e) { console.warn('[storage] setItem failed for', key, e); }
    },
    removeItem: function (key) {
        try { localStorage.removeItem(key); } catch (e) {}
    }
};
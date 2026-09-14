(function () {
    function getItem(key, fallback = []) {
        try { return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback)); }
        catch { return fallback; }
    }
    function setItem(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }
    OpenBox.Storage = { getItem, setItem };
})();
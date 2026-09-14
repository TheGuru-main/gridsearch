(function () {
    function esc(s) {
        return String(s || "").replace(/[&<>"']/g, function (c) {
            return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];
        });
    }

    function timeAgo(iso) {
        if (!iso) return "";
        var d = new Date(iso);
        var s = Math.floor((Date.now() - d.getTime()) / 1000);
        if (s < 60) return s + "s ago";
        if (s < 3600) return Math.floor(s / 60) + "m ago";
        if (s < 86400) return Math.floor(s / 3600) + "h ago";
        return Math.floor(s / 86400) + "d ago";
    }

    async function load() {
        var body = document.getElementById("newsBody");
        if (!body) return;
        body.innerHTML = '<p class="hint">Loading news...</p>';

        try {
            var res = await fetch("/api/news?category=sports&limit=25");
            var data = await res.json();
            var items = data.news || [];

            if (!items.length) {
                body.innerHTML =
                    '<p class="hint">' +
                    (data.note || data.error || "No news available right now.") +
                    "</p>";
                return;
            }

            body.innerHTML = '<div class="news-list">' + items.map(function (n) {
                return (
                    '<a class="news-card" href="' + esc(n.url) + '" target="_blank" rel="noopener">' +
                    (n.image ? '<div class="news-img" style="background-image:url(' + esc(n.image) + ')"></div>' : '') +
                    '<div class="news-body">' +
                    '<div class="news-source">' + esc(n.source || "") + " · " + timeAgo(n.published_at) + '</div>' +
                    '<h4 class="news-title">' + esc(n.title || "") + '</h4>' +
                    '<p class="news-desc">' + esc(n.description || "") + '</p>' +
                    '</div></a>'
                );
            }).join("") + "</div>";
        } catch (e) {
            body.innerHTML = '<p class="hint">Failed to load news: ' + esc(e.message) + '</p>';
        }
    }

    function show() {
        OpenBox.UI.showWorkspace("workspaceNews");
        load();
    }

    OpenBox.News = { show: show };
})();
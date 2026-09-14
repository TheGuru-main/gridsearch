(function () {
    function esc(s) {
        return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
            return ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[c];
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

        var res, data, rawText;
        try {
            res = await fetch("/api/news?category=sports&limit=25");
            rawText = await res.text();
            try { data = JSON.parse(rawText); } catch (e) { data = null; }
        } catch (err) {
            body.innerHTML = '<div class="err-box">' +
                '<strong>Network error</strong><br>' +
                esc(err.message) +
                '<br><br>Check that the backend is running and /api/news exists.' +
                '</div>';
            return;
        }

        if (!res.ok) {
            body.innerHTML = '<div class="err-box">' +
                '<strong>Backend returned HTTP ' + res.status + '</strong><br>' +
                esc(rawText.substring(0, 300)) +
                '<br><br>The /api/news route may not be deployed. Redeploy the backend.' +
                '</div>';
            return;
        }

        if (!data) {
            body.innerHTML = '<div class="err-box">' +
                '<strong>Backend did not return JSON</strong><br>' +
                esc(rawText.substring(0, 300)) +
                '</div>';
            return;
        }

        if (data.note) {
            body.innerHTML = '<div class="err-box">' +
                '<strong>Backend note:</strong><br>' +
                esc(data.note) +
                '<br><br>This usually means GNEWS_KEY is not set on Render.<br>' +
                'Add it under Environment, then redeploy.' +
                '</div>';
            return;
        }

        if (data.error) {
            body.innerHTML = '<div class="err-box">' +
                '<strong>Backend error:</strong><br>' +
                esc(data.error) +
                '</div>';
            return;
        }

        var items = data.news || [];
        if (!items.length) {
            body.innerHTML = '<div class="err-box">' +
                'Backend returned 0 articles. Possible reasons:<br>' +
                '· GNews free tier exhausted its 100/day quota<br>' +
                '· The category filter found nothing<br>' +
                '· The API key is invalid' +
                '</div>';
            return;
        }

        body.innerHTML = '<div class="news-list">' + items.map(function (n) {
            return '<a class="news-card" href="' + esc(n.url) + '" target="_blank" rel="noopener">' +
                (n.image ? '<div class="news-img" style="background-image:url(' + esc(n.image) + ')"></div>' : '') +
                '<div class="news-body">' +
                '<div class="news-source">' + esc(n.source || "") + " · " + timeAgo(n.published_at) + '</div>' +
                '<h4 class="news-title">' + esc(n.title || "") + '</h4>' +
                '<p class="news-desc">' + esc(n.description || "") + '</p>' +
                '</div></a>';
        }).join("") + "</div>";
    }

    function show() {
        OpenBox.UI.showWorkspace("workspaceNews");
        load();
    }

    document.addEventListener("DOMContentLoaded", function () {
        var btn = document.getElementById("btnNewsRefresh");
        if (btn) btn.addEventListener("click", function (e) { e.preventDefault(); load(); });
    });

    OpenBox.News = { show: show, load: load };
})();
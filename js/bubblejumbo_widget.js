/**
 * BubbleJumbo notification widget.
 * Shows small banners to users. Never shows the trap grid.
 */
(function () {
    const POLL_MS = 5000;
    const ENDPOINT = "/api/bj/notifications";

    function ensureContainer() {
        let el = document.getElementById("bj-notifications");
        if (!el) {
            el = document.createElement("div");
            el.id = "bj-notifications";
            el.style.cssText = `
                position: fixed; bottom: 20px; right: 20px; z-index: 9999;
                max-width: 340px; font-family: system-ui, sans-serif;
            `;
            document.body.appendChild(el);
        }
        return el;
    }

    function esc(s) {
        return String(s).replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;',
            '"': '&quot;', "'": '&#39;'
        })[c]);
    }

    function render(items) {
        const box = ensureContainer();
        if (!items || items.length === 0) {
            box.innerHTML = "";
            return;
        }
        box.innerHTML = items.slice(-3).reverse().map(n => `
            <div style="
                background:#12121a;border:1px solid #2a2a3d;
                border-left:4px solid ${n.severity === 'high' ? '#ff6b6b' : '#00d2ff'};
                border-radius:8px;padding:12px;margin-top:8px;color:#e8e8f0;
                box-shadow:0 4px 16px rgba(0,0,0,0.4);font-size:13px;line-height:1.4;
            ">
                <strong style="color:#00d2ff;display:block;margin-bottom:4px;">
                    ${esc(n.type || 'Security')}
                </strong>
                <span>${esc(n.message || '')}</span>
                <div style="margin-top:6px;font-size:11px;color:#555570;">
                    ${new Date((n.time || 0) * 1000).toLocaleTimeString()}
                </div>
            </div>`).join("");
    }

    async function poll() {
        try {
            const r = await fetch(ENDPOINT, { credentials: "include" });
            const data = await r.json();
            render(data.notifications || []);
        } catch (_) {
            // silent — never interrupt the user
        }
    }

    // Exposed helper for the frontend to call when it detects phishing
    window.bjReportPhishing = async function (url) {
        try {
            await fetch("/api/bj/mark-suspicious", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url }),
            });
        } catch (_) {}
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", poll);
    } else {
        poll();
    }
    setInterval(poll, POLL_MS);
})();
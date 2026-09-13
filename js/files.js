(function () {
    async function loadCategory(category) {
        const grid = document.getElementById('categoryGrid');
        grid.innerHTML = '<p class="hint">Loading...</p>';
        const r = await OpenBox.API.items(category);
        if (!r.ok) { grid.innerHTML = '<p class="hint">Failed to load.</p>'; return; }
        const items = r.data.items || [];
        if (!items.length) {
            grid.innerHTML = '<p class="hint">No files in this category.</p>';
            return;
        }
        grid.innerHTML = items.map(f => {
            const mb = (f.file_size / (1024 * 1024)).toFixed(2);
            const icon = OpenBox.GSP.getFileIcon(f.category);
            return `
                <div class="file-card" data-id="${f.id}">
                    <div class="icon">${icon}</div>
                    <div class="info">
                        <h4>${escapeHtml(f.title)}</h4>
                        <small>📁 ${String.fromCharCode(65 + f.gsp_col)}${f.gsp_row} · ${mb} MB</small>
                        <small>💰 ${f.price_byflints} byflints</small>
                    </div>
                    <div class="actions">
                        <a href="#" class="action-download" data-id="${f.id}">⬇️</a>
                    </div>
                </div>
            `;
        }).join('');

        grid.querySelectorAll('.file-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.closest('.action-download')) return;
                openDetail(card.dataset.id);
            });
        });
        grid.querySelectorAll('.action-download').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                download(btn.dataset.id);
            });
        });
    }

    async function openDetail(id) {
        const r = await OpenBox.API.itemDetail(id);
        if (!r.ok) return alert('Failed to load');
        const f = r.data;
        document.getElementById('detailTitle').textContent = f.title;
        document.getElementById('detailContent').innerHTML = `
            <p><strong>Category:</strong> ${f.category}</p>
            <p><strong>Size:</strong> ${(f.file_size / (1024*1024)).toFixed(2)} MB</p>
            <p><strong>Grid:</strong> ${String.fromCharCode(65 + f.gsp_col)}${f.gsp_row}</p>
            <p><strong>Uploader:</strong> ${f.uploader}</p>
            <p><strong>Price:</strong> ${f.price_byflints} byflints</p>
            <p><strong>Downloads:</strong> ${f.downloads}</p>
            <a href="#" class="primary-btn" data-action="download" data-id="${f.id}">⬇️ Download</a>
        `;
        document.getElementById('detailContent').querySelector('[data-action="download"]')
            .addEventListener('click', (e) => { e.preventDefault(); download(f.id); });
        OpenBox.UI.showWorkspace('detailScreen');
    }

    async function download(id) {
        const r = await OpenBox.API.itemDownload(id);
        if (!r.ok) return alert(r.data.detail || 'Download failed');
        window.location.href = r.data.download_url;
        OpenBox.Wallet.refresh();
    }

    function closeDetail() { OpenBox.UI.showWorkspace('workspaceHome'); }

    function updateFee() {
        const cat = document.getElementById('uploadCategory').value;
        const fee = OpenBox.CONFIG.UPLOAD_FEE[cat] || 5;
        document.getElementById('feeDisplay').textContent = `Fee: ${fee} byflints`;
    }

    async function doUpload() {
        const fileInput = document.getElementById('fileInput');
        const category = document.getElementById('uploadCategory').value;
        const title = document.getElementById('filenameInput').value.trim() || fileInput.files[0]?.name;
        const price = parseFloat(document.getElementById('priceByflint').value) || 0;
        const description = document.getElementById('description').value;
        const agreement = document.getElementById('originalityAgreement').checked;

        if (!fileInput.files.length) return alert('Choose file');
        if (!title) return alert('Title required');
        if (!agreement) return alert('Confirm originality');

        const fd = new FormData();
        fd.append('title', title);
        fd.append('kind', category);
        fd.append('category', category);
        fd.append('description', description);
        fd.append('price_byflints', price);
        fd.append('file', fileInput.files[0]);

        document.getElementById('uploadStatus').textContent = 'Uploading...';
        const r = await OpenBox.API.itemUpload(fd);
        if (!r.ok) {
            document.getElementById('uploadStatus').textContent = '';
            return alert(r.data.detail || 'Upload failed');
        }
        alert('Uploaded!');
        document.getElementById('fileInput').value = '';
        document.getElementById('filenameInput').value = '';
        document.getElementById('description').value = '';
        document.getElementById('uploadStatus').textContent = '';
        OpenBox.Wallet.refresh();
        OpenBox.UI.showWorkspace('workspaceHome');
        loadCategory(OpenBox.App.currentCategory);
    }

    async function search() {
        const q = document.getElementById('searchQuery').value.trim().toLowerCase();
        if (!q) { document.getElementById('searchResults').style.display = 'none'; return; }
        const r = await OpenBox.API.items();
        const results = (r.data.items || []).filter(f => f.title.toLowerCase().includes(q));
        const box = document.getElementById('searchResults');
        box.style.display = 'block';
        box.innerHTML = results.length
            ? results.map(f => `<div class="file-card"><div class="info"><h4>${escapeHtml(f.title)}</h4><small>${f.price_byflints} byflints</small></div></div>`).join('')
            : '<p class="hint">No results.</p>';
    }

    function escapeHtml(s) {
        return String(s || '').replace(/[&<>"']/g, c => ({
            '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
        })[c]);
    }

    OpenBox.Files = { loadCategory, openDetail, closeDetail, download, updateFee, doUpload, search };
})();
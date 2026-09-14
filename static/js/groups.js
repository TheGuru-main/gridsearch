(function () {
    function getItem(key, fallback) {
        try { return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback || [])); }
        catch (e) { return fallback || []; }
    }
    function setItem(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }

    function me() {
        return OpenBox?.App?.currentUser || null;
    }
    function myPhone() {
        return me()?.phone || '';
    }
    function myName() {
        return me()?.fullName || myPhone();
    }

    function showMyHome() {
        OpenBox.UI.showWorkspace('workspaceMyHome');
        renderGroups();
    }

    function renderGroups() {
        var groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []);
        var container = document.getElementById('groupsList');
        if (!container) return;

        if (!groups.length) {
            container.innerHTML = '<p class="hint">No groups yet. Create one or join with an invite code.</p>';
            return;
        }

        container.innerHTML = groups.map(function (g) {
            var mine = (g.members || []).indexOf(myPhone()) !== -1;
            return '<a href="#" class="group-item" data-action="open-group" data-group-id="' + g.id + '">' +
                '<strong>' + escapeHtml(g.name) + '</strong>' +
                '<small>📁 ' + String.fromCharCode(65 + (g.gspCol || 0)) + (g.gspRow || 1) +
                ' · ' + (g.members || []).length + ' member' + ((g.members || []).length === 1 ? '' : 's') +
                (mine ? '' : ' · <em>not joined</em>') +
                '</small></a>';
        }).join('');

        container.querySelectorAll('.group-item').forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                openGroupDetail(el.dataset.groupId);
            });
        });
    }

    function createGroup() {
        var name = prompt('Group name:');
        if (!name) return;
        name = name.trim();
        if (!name) return;
        if (!myPhone()) return alert('Please sign in first.');

        var groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []);
        var col = (name.replace(/[^a-z]/gi, '').length) % 4;
        var group = {
            id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
            name: name,
            owner: myPhone(),
            ownerName: myName(),
            gspCol: col,
            gspRow: 1,
            posts: [],
            members: [myPhone()],
            createdAt: new Date().toISOString()
        };
        groups.push(group);
        setItem(OpenBox.CONFIG.GROUPS_KEY, groups);
        renderGroups();
        openGroupDetail(group.id);
    }

    function joinGroup() {
        var input = document.getElementById('inviteCodeInput');
        var code = (input?.value || '').trim();
        if (!code) return alert('Enter invite code');
        if (!myPhone()) return alert('Please sign in first.');

        var groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []);
        var group = groups.find(function (g) { return g.id === code; });
        if (!group) return alert('Group not found');

        if (!group.members) group.members = [];
        if (group.members.indexOf(myPhone()) === -1) {
            group.members.push(myPhone());
            setItem(OpenBox.CONFIG.GROUPS_KEY, groups);
        }
        if (input) input.value = '';
        renderGroups();
        openGroupDetail(group.id);
    }

    function openGroupDetail(groupId) {
        var groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []);
        var group = groups.find(function (g) { return g.id === groupId; });
        if (!group) return alert('Group not found');

        var titleEl = document.getElementById('groupDetailTitle');
        var infoEl = document.getElementById('groupDetailInfo');
        var postsEl = document.getElementById('groupPostsList');

        if (titleEl) titleEl.textContent = group.name;
        if (infoEl) {
            infoEl.innerHTML =
                '<p><strong>Owner:</strong> ' + escapeHtml(group.ownerName || group.owner) + '</p>' +
                '<p><strong>GSP Cell:</strong> ' +
                String.fromCharCode(65 + (group.gspCol || 0)) + (group.gspRow || 1) + '</p>' +
                '<p><strong>Members:</strong> ' + (group.members || []).length + '</p>' +
                '<p><strong>Invite code:</strong> <code>' + escapeHtml(group.id) + '</code></p>';
        }
        if (postsEl) {
            postsEl.innerHTML = (group.posts && group.posts.length)
                ? group.posts.map(function (p) {
                    return '<div class="group-post">' +
                        '<strong>' + escapeHtml(p.authorName || p.author) + '</strong>: ' +
                        escapeHtml(p.text) +
                        '<small>' + new Date(p.timestamp).toLocaleString() + '</small></div>';
                }).join('')
                : '<p class="hint">No posts yet.</p>';
        }

        OpenBox.App.currentGroupId = groupId;
        OpenBox.UI.showWorkspace('workspaceGroupDetail');
    }

    function addPostToGroup() {
        var gid = OpenBox.App.currentGroupId;
        var input = document.getElementById('groupPostInput');
        var text = (input?.value || '').trim();
        if (!gid || !text) return;

        var groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []);
        var group = groups.find(function (g) { return g.id === gid; });
        if (!group) return;

        group.posts = group.posts || [];
        group.posts.push({
            author: myPhone(),
            authorName: myName(),
            text: text,
            timestamp: new Date().toISOString()
        });
        setItem(OpenBox.CONFIG.GROUPS_KEY, groups);
        if (input) input.value = '';
        openGroupDetail(gid);
    }

    function closeGroupDetail() {
        OpenBox.UI.showWorkspace('workspaceMyHome');
        renderGroups();
    }

    function escapeHtml(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
        });
    }

    OpenBox.Groups = {
        showMyHome: showMyHome,
        createGroup: createGroup,
        joinGroup: joinGroup,
        openGroupDetail: openGroupDetail,
        addPostToGroup: addPostToGroup,
        closeGroupDetail: closeGroupDetail
    };
})();
(function () {
    const { getItem, setItem } = OpenBox.Storage;

    function getUserByPhone(phone) {
        return (getItem(OpenBox.CONFIG.USERS_KEY, []) || []).find(u => u.phone === phone);
    }

    function showMyHome() {
        OpenBox.UI.showWorkspace('workspaceMyHome');
        renderGroups();
    }

    function renderGroups() {
        const groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []) || [];
        const container = document.getElementById('groupsList');
        container.innerHTML = groups.length
            ? groups.map(g => `
                <a href="#" class="group-item" data-action="open-group" data-group-id="${g.id}">
                    <strong>${g.name}</strong><br>
                    <small>📁 ${String.fromCharCode(65 + g.gspCol)}${g.gspRow}</small>
                </a>`).join('')
            : '<p class="hint">No groups yet.</p>';
    }

    function createGroup() {
        const name = prompt('Group name:');
        if (!name) return;
        const me = OpenBox.App.currentUser?.phone;
        const groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []) || [];
        const col = OpenBox.GSP.nameLength(name) % 4;
        const group = {
            id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
            name,
            owner: me,
            gspCol: col,
            gspRow: 1,
            posts: [],
            members: [me],
            createdAt: new Date().toISOString()
        };
        groups.push(group);
        setItem(OpenBox.CONFIG.GROUPS_KEY, groups);
        renderGroups();
        openGroupDetail(group.id);
    }

    function joinGroup() {
        const code = document.getElementById('inviteCodeInput').value.trim();
        if (!code) return alert('Enter invite code');
        const groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []) || [];
        const group = groups.find(g => g.id === code);
        if (!group) return alert('Group not found');
        const me = OpenBox.App.currentUser?.phone;
        if (!group.members.includes(me)) {
            group.members.push(me);
            setItem(OpenBox.CONFIG.GROUPS_KEY, groups);
        }
        renderGroups();
        openGroupDetail(group.id);
    }

    function openGroupDetail(groupId) {
        const groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []) || [];
        const group = groups.find(g => g.id === groupId);
        if (!group) return;
        document.getElementById('groupDetailTitle').textContent = group.name;
        document.getElementById('groupDetailInfo').innerHTML = `
            <p><strong>Owner:</strong> ${getUserByPhone(group.owner)?.fullName || group.owner}</p>
            <p><strong>GSP Cell:</strong> ${String.fromCharCode(65 + group.gspCol)}${group.gspRow}</p>
            <p><strong>Members:</strong> ${group.members.length}</p>
        `;
        document.getElementById('groupPostsList').innerHTML = group.posts.length
            ? group.posts.map(p => `
                <div class="group-post">
                    <strong>${p.authorName || p.author}</strong>: ${p.text}
                    <small>${new Date(p.timestamp).toLocaleString()}</small>
                </div>`).join('')
            : '<p class="hint">No posts yet.</p>';
        OpenBox.UI.showWorkspace('workspaceGroupDetail');
        OpenBox.App.currentGroupId = groupId;
    }

    function addPostToGroup() {
        const gid = OpenBox.App.currentGroupId;
        const text = document.getElementById('groupPostInput').value.trim();
        if (!gid || !text) return;
        const groups = getItem(OpenBox.CONFIG.GROUPS_KEY, []) || [];
        const group = groups.find(g => g.id === gid);
        if (!group) return;
        const me = OpenBox.App.currentUser?.phone;
        const u = getUserByPhone(me);
        group.posts.push({
            author: me,
            authorName: u?.fullName || me,
            text,
            timestamp: new Date().toISOString()
        });
        setItem(OpenBox.CONFIG.GROUPS_KEY, groups);
        document.getElementById('groupPostInput').value = '';
        openGroupDetail(gid);
    }

    function closeGroupDetail() {
        OpenBox.UI.showWorkspace('workspaceMyHome');
        renderGroups();
    }

    OpenBox.Groups = { showMyHome, createGroup, joinGroup, openGroupDetail, addPostToGroup, closeGroupDetail };
})();
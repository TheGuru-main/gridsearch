(function () {
    function showWorkspace(id) {
        document.querySelectorAll('.workspace').forEach(w => w.classList.remove('active'));
        const el = document.getElementById(id);
        if (el) el.classList.add('active');
        const nav = document.getElementById('bottomNav');
        if (nav) nav.style.display = (id === 'authScreen') ? 'none' : 'flex';
    }

    document.addEventListener('click', (e) => {
        const el = e.target.closest('a');
        if (!el) return;
        e.preventDefault();

        const workspace = el.dataset.workspace;
        if (workspace) {
            showWorkspace(workspace);
            document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
            el.classList.add('active');
            if (workspace === 'workspaceHome') OpenBox.Files.loadCategory(OpenBox.App.currentCategory);
            if (workspace === 'workspaceMyHome') OpenBox.Groups.showMyHome();
            if (workspace === 'workspaceMessages') OpenBox.Messages.show();
            if (workspace === 'workspaceWallet') OpenBox.Wallet.show();
            if (workspace === 'workspaceFantasy') OpenBox.Fantasy.show();
            return;
        }

        const authTab = el.dataset.authTab;
        if (authTab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            document.querySelectorAll('.auth-pane').forEach(p => p.classList.remove('active'));
            document.getElementById(authTab + 'Pane').classList.add('active');
            return;
        }

        const category = el.dataset.category;
        if (category) {
            document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            OpenBox.App.currentCategory = category;
            OpenBox.Files.loadCategory(category);
            document.getElementById('searchResults').style.display = 'none';
            return;
        }

        switch (el.id) {
            case 'btnLogin': OpenBox.Auth.login(); break;
            case 'btnSignup': OpenBox.Auth.signup(); break;
            case 'btnLogout': OpenBox.Auth.logout(); break;
            case 'btnRefresh': OpenBox.Files.loadCategory(OpenBox.App.currentCategory); break;
            case 'btnSearch': OpenBox.Files.search(); break;
            case 'btnUpload': OpenBox.Files.doUpload(); break;
            case 'btnCloseUpload': showWorkspace('workspaceHome'); break;
            case 'btnCloseDetail': OpenBox.Files.closeDetail(); break;
            case 'btnCloseChat': OpenBox.Messages.closeChat(); break;
            case 'btnSendMessage': OpenBox.Messages.sendMessage(); break;
            case 'btnCreateGroup': OpenBox.Groups.createGroup(); break;
            case 'btnJoinGroup': OpenBox.Groups.joinGroup(); break;
            case 'btnCloseGroupDetail': OpenBox.Groups.closeGroupDetail(); break;
            case 'btnAddGroupPost': OpenBox.Groups.addPostToGroup(); break;
            case 'btnCloseRules': document.getElementById('rulesModal').style.display = 'none'; break;
            case 'btnCloseCheckout': document.getElementById('checkoutModal').style.display = 'none'; break;
            default:
                const action = el.dataset.action;
                if (action === 'show-rules') document.getElementById('rulesModal').style.display = 'flex';
                else if (action === 'download') OpenBox.Files.download(el.dataset.id);
                else if (action === 'open-chat') OpenBox.Messages.openChat(el.dataset.phone);
                else if (action === 'open-group') OpenBox.Groups.openGroupDetail(el.dataset.groupId);
        }
    });

    OpenBox.UI = { showWorkspace };
})();
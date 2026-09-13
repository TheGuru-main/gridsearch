(function () {
    async function afterLogin() {
        // Refresh wallet
        await OpenBox.Wallet.refresh();
        // Load default category
        OpenBox.Files.loadCategory('app');
        // Go home
        OpenBox.UI.showWorkspace('workspaceHome');
    }

    document.addEventListener('DOMContentLoaded', async () => {
        // Sync upload fee display
        const cat = document.getElementById('uploadCategory');
        if (cat) cat.addEventListener('change', OpenBox.Files.updateFee);
        OpenBox.Files.updateFee();

        // Try to restore session
        const me = await OpenBox.API.me();
        if (me.ok) {
            OpenBox.App.currentUser = {
                phone: me.data.phone,
                fullName: me.data.full_name,
                byflints: me.data.byflints
            };
            await afterLogin();
        } else {
            OpenBox.UI.showWorkspace('authScreen');
        }
    });

    OpenBox.App.afterLogin = afterLogin;
})();
(function () {
    const { getItem, setItem } = OpenBox.Storage;
    let activeChat = null;

    function getUserByPhone(phone) {
        return (getItem(OpenBox.CONFIG.USERS_KEY, []) || []).find(u => u.phone === phone);
    }

    function calculateStartRow(phone) {
        const users = getItem(OpenBox.CONFIG.USERS_KEY, []);
        const user = users.find(u => u.phone === phone);
        if (!user) return 0;
        return OpenBox.GSP.userStartRow(user.fullName, user.phone);
    }

    function show() {
        OpenBox.UI.showWorkspace('workspaceMessages');
        loadConversations();
    }

    function loadConversations() {
        const me = OpenBox.App.currentUser?.phone;
        const users = (getItem(OpenBox.CONFIG.USERS_KEY, []) || []).filter(u => u.phone !== me);
        const container = document.getElementById('conversationList');
        container.innerHTML = users.length
            ? users.map(u => `
                <a href="#" class="conversation-item" data-action="open-chat" data-phone="${u.phone}">
                    <strong>${u.fullName || u.phone}</strong><br>
                    <small>${u.phone}</small>
                </a>`).join('')
            : '<p class="hint">No other users yet.</p>';
    }

    function openChat(phone) {
        activeChat = phone;
        document.getElementById('conversationList').style.display = 'none';
        document.getElementById('chatView').style.display = 'flex';
        document.getElementById('btnCloseChat').style.display = 'block';
        const u = getUserByPhone(phone);
        document.getElementById('chatPartner').textContent = u?.fullName || phone;
        loadChatMessages(phone);
    }

    function closeChat() {
        document.getElementById('chatView').style.display = 'none';
        document.getElementById('btnCloseChat').style.display = 'none';
        document.getElementById('conversationList').style.display = 'block';
        document.getElementById('chatPartner').textContent = 'Messages';
        activeChat = null;
    }

    function loadChatMessages(phone) {
        const me = OpenBox.App.currentUser?.phone;
        const msgs = (getItem(OpenBox.CONFIG.MSGS_KEY, []) || [])
            .filter(m => (m.from === me && m.to === phone) || (m.from === phone && m.to === me))
            .sort((a,b) => new Date(a.timestamp) - new Date(b.timestamp));
        const container = document.getElementById('chatMessages');
        container.innerHTML = msgs.map(m => `
            <div class="chat-message ${m.from === me ? 'sent' : 'received'}">
                ${m.body}
                <small>to row ${m.to_start_row || ''} · ${new Date(m.timestamp).toLocaleString()}</small>
            </div>`).join('');
        container.scrollTop = container.scrollHeight;
    }

    function sendMessage() {
        const body = document.getElementById('messageInput').value.trim();
        if (!body || !activeChat) return;
        const me = OpenBox.App.currentUser?.phone;
        const msgs = getItem(OpenBox.CONFIG.MSGS_KEY, []) || [];
        msgs.push({
            from: me,
            to: activeChat,
            body,
            from_start_row: calculateStartRow(me),
            to_start_row: calculateStartRow(activeChat),
            timestamp: new Date().toISOString()
        });
        setItem(OpenBox.CONFIG.MSGS_KEY, msgs);
        document.getElementById('messageInput').value = '';
        loadChatMessages(activeChat);
    }

    OpenBox.Messages = { show, closeChat, openChat, loadChatMessages, sendMessage };
})();
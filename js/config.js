window.OpenBox = window.OpenBox || {};
OpenBox.CONFIG = {
    SESSION_KEY: 'openbox_session',
    MSGS_KEY: 'openbox_messages',
    GROUPS_KEY: 'openbox_groups',
    ESCROW_KEY: 'openbox_escrows',
    UNIVERSAL_UID: "550198550199",
    WELCOME_BYFLINTS: 1070,
    UPLOAD_FEE: { app: 15, game: 20, video: 10, other: 5 },
    DOWNLOAD_FEE: 3,
    UPLOADER_SHARE: 2.5,
    CATEGORY_COL: { app: 0, game: 1, video: 2, other: 3 },
    DAILY_REWARD: 5,
    STREAK_TARGET_DAYS: 5,
    STREAK_BONUS: 200
};
OpenBox.App = {
    currentUser: null,
    currentCategory: 'app',
    currentGroupId: null,
};
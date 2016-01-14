module.exports = {

    DEBUG: <%= DEBUG %>,

    INPUT_DELAY_BEFORE_SAVE: 500, // in milliseconds

    SITE_TITLE: 'Sana Protocol Builder',

    APP_NAMESPACE: 'spb',

    API_BASE: '<%= API_BASE %>',

    LOCALES_SUPPORTED: [
        'en'
    ],

    NON_AUTH_PAGES: [
        'login',
        'signup',
        'terms',
        'privacy',
    ],

    ELEMENT_NAMES: {
        DATE: "Date",
        ENTRY: "Entry",
        SELECT: "Selection",
        MULTI_SELECT: "Multiple Choice",
        RADIO: "Single Choice",
        PICTURE: "Picture",
        PLUGIN: "Plugin (file)",
        PLUGIN_ENTRY: "Plugin (entry)",
    },

};
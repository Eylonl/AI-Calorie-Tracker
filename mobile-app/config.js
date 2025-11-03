// CalorieAI PWA Configuration
// Replace these with your actual Supabase credentials

const CONFIG = {
    // Backend API Configuration
    STREAMLIT_API_URL: 'https://ai-calorie-tracker-eylonl.streamlit.app',
    
    // These will be fetched from the backend API
    SUPABASE_URL: null,
    SUPABASE_ANON_KEY: null,
    
    // App Configuration
    APP_NAME: 'CalorieAI',
    VERSION: '1.0.0',
    
    // Features - Will be configured by backend
    FEATURES: {
        SUPABASE_ENABLED: false,
        AI_ANALYSIS_ENABLED: false,
        OFFLINE_MODE: true,
        USE_BACKEND_API: true  // Use Streamlit backend for API calls
    }
};

// Export for use in main app
window.CONFIG = CONFIG;

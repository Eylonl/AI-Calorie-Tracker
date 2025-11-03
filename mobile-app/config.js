// CalorieAI PWA Configuration
// Replace these with your actual Supabase credentials

const CONFIG = {
    // Backend API Configuration
    STREAMLIT_API_URL: 'https://ai-calorie-tracker-eylonl.streamlit.app',
    
    // Supabase Configuration - Add your credentials here to bypass CORS
    // TODO: Replace with your actual Supabase credentials
    SUPABASE_URL: 'https://your-project.supabase.co',
    SUPABASE_ANON_KEY: 'your-supabase-anon-key-here',
    
    // App Configuration
    APP_NAME: 'CalorieAI',
    VERSION: '1.0.0',
    
    // Features
    FEATURES: {
        SUPABASE_ENABLED: false, // Set to true after adding your credentials above
        AI_ANALYSIS_ENABLED: false, // AI will still use backend API
        OFFLINE_MODE: true,
        USE_BACKEND_API: true  // Use Streamlit backend for AI calls only
    }
};

// Export for use in main app
window.CONFIG = CONFIG;

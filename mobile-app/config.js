// CalorieAI PWA Configuration
// Replace these with your actual Supabase credentials

const CONFIG = {
    // Backend API Configuration
    STREAMLIT_API_URL: 'https://ai-calorie-tracker-eylonl.streamlit.app',
    
    // Supabase Configuration - Add your credentials here to bypass CORS
    // TODO: Replace with your actual Supabase credentials
    SUPABASE_URL: 'https://tchmxyoetjsujxszohtf.supabase.co',
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjaG14eW9ldGpzdWp4c3pvaHRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUyMzA1ODEsImV4cCI6MjA3MDgwNjU4MX0.gaZcAtXpX3nFwCZJkHNvircwG2WQduehWE3Yv_pCz9c',
    
    // App Configuration
    APP_NAME: 'CalorieAI',
    VERSION: '1.0.0',
    
    // Features
    FEATURES: {
        SUPABASE_ENABLED: true, // Set to true after adding your credentials above
        AI_ANALYSIS_ENABLED: false, // AI analysis disabled - no mock data
        OFFLINE_MODE: true,
        USE_BACKEND_API: false  // Backend API disabled due to CORS issues
    }
};

// Export for use in main app
window.CONFIG = CONFIG;

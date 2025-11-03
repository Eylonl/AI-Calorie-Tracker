// CalorieAI PWA Configuration
// Replace these with your actual Supabase credentials

const CONFIG = {
    // Backend API Configuration
    STREAMLIT_API_URL: 'https://ai-calorie-tracker-eylonl.streamlit.app',
    
    // Supabase Configuration - Add your credentials here to bypass CORS
    // TODO: Replace with your actual Supabase credentials
    SUPABASE_URL: 'https://enamodyuntmxqhjfhgmt.supabase.co',
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVuYW1vZHl1bnRteHFoamZoZ210Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIxMDMyNzQsImV4cCI6MjA3NzY3OTI3NH0.UQExdZDJzh_1CgUzDuLJRvxJs4_V6x1izQfueFaw1QQ',
    
    // App Configuration
    APP_NAME: 'CalorieAI',
    VERSION: '1.0.0',
    
    // Vercel API Configuration
    VERCEL_API_URL: 'https://ai-calorie-tracker-git-main-eylonls-projects.vercel.app',
    
    // Features
    FEATURES: {
        SUPABASE_ENABLED: true,
        AI_ANALYSIS_ENABLED: true, // AI analysis enabled via Vercel
        OFFLINE_MODE: true,
        USE_BACKEND_API: true,  // Use Vercel serverless functions
        USE_VERCEL_API: true    // Use Vercel instead of Streamlit
    }
};

// Export for use in main app
window.CONFIG = CONFIG;

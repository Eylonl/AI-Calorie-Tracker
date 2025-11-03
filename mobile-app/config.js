// CalorieAI PWA Configuration
// Replace these with your actual Supabase credentials

const CONFIG = {
    // Supabase Configuration
    SUPABASE_URL: 'https://your-project.supabase.co',
    SUPABASE_ANON_KEY: 'your-supabase-anon-key-here',
    
    // OpenAI Configuration (for future AI integration)
    OPENAI_API_KEY: 'your-openai-api-key-here',
    
    // App Configuration
    APP_NAME: 'CalorieAI',
    VERSION: '1.0.0',
    
    // Features
    FEATURES: {
        SUPABASE_ENABLED: false, // Set to true when you add credentials
        AI_ANALYSIS_ENABLED: false, // Set to true when you add OpenAI key
        OFFLINE_MODE: true
    }
};

// Export for use in main app
window.CONFIG = CONFIG;

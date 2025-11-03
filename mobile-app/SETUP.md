# CalorieAI PWA Setup Guide

## 🚀 Connect Supabase for Full Functionality

### Step 1: Get Your Supabase Credentials

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your CalorieAI project**
3. **Go to Settings** → **API**
4. **Copy these values:**
   - **Project URL** (looks like: `https://abcdefgh.supabase.co`)
   - **anon/public key** (long string starting with `eyJ...`)

### Step 2: Update config.js

1. **Open**: `mobile-app/config.js`
2. **Replace** the placeholder values:

```javascript
const CONFIG = {
    // Replace these with YOUR actual credentials
    SUPABASE_URL: 'https://your-actual-project.supabase.co',
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    
    // Enable Supabase features
    FEATURES: {
        SUPABASE_ENABLED: true,  // Change to true
        AI_ANALYSIS_ENABLED: false,
        OFFLINE_MODE: true
    }
};
```

### Step 3: Update Your Database Schema

Make sure your Supabase database has the nutrition columns:

```sql
-- Run this in your Supabase SQL Editor
ALTER TABLE public.foods 
ADD COLUMN IF NOT EXISTS protein DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS carbs DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS fat DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS fiber DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS sugar DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS sodium DECIMAL(8,2) DEFAULT 0;
```

### Step 4: Test the Connection

1. **Save the config.js file**
2. **Refresh your PWA**
3. **Check browser console** for "Supabase initialized successfully"
4. **Try logging a meal** - it should save to your database
5. **Check history tab** - should load real data from Supabase

## ✅ What You'll Get After Setup:

- **Real data sync** between PWA and Streamlit app
- **Cloud storage** for meal photos
- **Persistent meal history** across devices
- **Full CRUD operations** (Create, Read, Update, Delete)
- **Nutrition tracking** with all your data

## 🔧 Optional: Enable AI Analysis

To enable AI photo analysis, also add your OpenAI API key:

```javascript
OPENAI_API_KEY: 'sk-your-openai-api-key-here',
FEATURES: {
    SUPABASE_ENABLED: true,
    AI_ANALYSIS_ENABLED: true,  // Enable this too
    OFFLINE_MODE: true
}
```

## 🚨 Security Note

Your anon/public key is safe to use in client-side code. It only allows operations permitted by your Row Level Security (RLS) policies.

## 📱 After Setup

Your PWA will have the same data as your Streamlit app, but with a much better mobile experience!

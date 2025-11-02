# 🚀 Supabase Setup Guide for AI Calorie Tracker

Follow these steps to set up Supabase cloud storage for your calorie tracker app.

## 📋 Prerequisites
- Supabase account (free tier available)
- Your calorie tracker app repository

## 🛠️ Step 1: Create Supabase Project

1. **Go to [Supabase Dashboard](https://supabase.com/dashboard)**
2. **Click "New Project"**
3. **Fill in project details:**
   - Organization: Select your organization
   - Name: `ai-calorie-tracker` (or your preferred name)
   - Database Password: Generate a strong password
   - Region: Choose closest to your location
4. **Click "Create new project"**
5. **Wait for project to be ready** (2-3 minutes)

## 🗄️ Step 2: Set Up Database Schema

1. **Go to SQL Editor** in your Supabase dashboard
2. **Copy the entire contents** of `supabase_schema.sql`
3. **Paste and run** the SQL commands
4. **Verify tables created:**
   - Go to Table Editor
   - You should see `meals` and `foods` tables

## 🔧 Step 3: Configure Storage

1. **Go to Storage** in Supabase dashboard
2. **Verify bucket created:**
   - You should see `meal-photos` bucket
   - If not, create it manually with public access

## 🔑 Step 4: Get API Credentials

1. **Go to Settings > API** in Supabase dashboard
2. **Copy these values:**
   - **Project URL** (looks like: `https://abcdefgh.supabase.co`)
   - **Anon public key** (long string starting with `eyJ...`)

## ⚙️ Step 5: Configure Streamlit Secrets

### For Local Development:
1. **Create `.streamlit/secrets.toml`** in your project directory
2. **Add your credentials:**
```toml
OPENAI_API_KEY = "your-openai-api-key"
APP_PASSWORD = "your-app-password"

# Supabase Configuration
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
```

### For Streamlit Community Cloud:
1. **Go to your deployed app** settings
2. **Add secrets** in the deployment configuration:
```toml
OPENAI_API_KEY = "your-openai-api-key"
APP_PASSWORD = "your-app-password"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
```

## 🚀 Step 6: Deploy Updated App

1. **Commit and push** your changes to GitHub
2. **Streamlit Community Cloud** will automatically redeploy
3. **Check the sidebar** - you should see "☁️ Connected to Supabase Cloud"

## ✅ Step 7: Test the Integration

1. **Take a photo** of a meal
2. **Analyze and save** the meal
3. **Check Supabase dashboard:**
   - Go to Table Editor > meals (should see your meal)
   - Go to Storage > meal-photos (should see your photo)

## 🔄 Step 8: Data Migration (Optional)

If you have existing meal data in local storage:

1. **The app will automatically detect** Supabase connection
2. **Your old data** remains in local storage as backup
3. **New meals** will be saved to Supabase
4. **To migrate old data:** Use the migration feature in the app (coming soon)

## 🎯 Benefits You'll Get

✅ **Persistent Storage** - Data never lost on app restarts
✅ **Photo Storage** - Actual meal photos saved with analysis
✅ **Cloud Backup** - Automatic backups and reliability
✅ **Multi-device Access** - Access your data from anywhere
✅ **Scalability** - Handles unlimited meals and photos

## 🆘 Troubleshooting

**"Failed to connect to Supabase":**
- Check your URL and API key are correct
- Ensure no extra spaces in secrets.toml
- Verify your Supabase project is active

**"Failed to save to cloud":**
- Check your internet connection
- Verify Supabase project isn't paused (free tier limitation)
- Check Supabase dashboard for any issues

**Photos not appearing:**
- Verify storage bucket `meal-photos` exists
- Check bucket is set to public access
- Ensure storage policies are correctly configured

## 📞 Support

If you encounter issues:
1. Check the Supabase dashboard for error logs
2. Verify all SQL commands ran successfully
3. Ensure API credentials are correctly configured
4. The app will fall back to local storage if Supabase fails

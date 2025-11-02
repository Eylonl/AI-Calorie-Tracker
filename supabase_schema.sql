-- Supabase Database Schema for AI Calorie Tracker
-- Run these commands in your Supabase SQL Editor

-- Enable Row Level Security
ALTER TABLE IF EXISTS public.meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.foods ENABLE ROW LEVEL SECURITY;

-- Create meals table
CREATE TABLE IF NOT EXISTS public.meals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default_user', -- For future user authentication
    date DATE NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    meal_type TEXT NOT NULL CHECK (meal_type IN ('Breakfast', 'Lunch', 'Dinner', 'Snack')),
    total_calories INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    photo_url TEXT, -- URL to stored photo in Supabase Storage
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create foods table (related to meals)
CREATE TABLE IF NOT EXISTS public.foods (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    meal_id UUID REFERENCES public.meals(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    portion_size TEXT NOT NULL,
    calories INTEGER NOT NULL DEFAULT 0,
    protein DECIMAL(8,2) DEFAULT 0,     -- grams
    carbs DECIMAL(8,2) DEFAULT 0,       -- grams  
    fat DECIMAL(8,2) DEFAULT 0,         -- grams
    fiber DECIMAL(8,2) DEFAULT 0,       -- grams
    sugar DECIMAL(8,2) DEFAULT 0,       -- grams
    sodium DECIMAL(8,2) DEFAULT 0,      -- milligrams
    confidence INTEGER DEFAULT 100 CHECK (confidence >= 0 AND confidence <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_meals_user_date ON public.meals(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_meals_timestamp ON public.meals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_foods_meal_id ON public.foods(meal_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS update_meals_updated_at ON public.meals;
CREATE TRIGGER update_meals_updated_at
    BEFORE UPDATE ON public.meals
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Row Level Security Policies (for future user authentication)
-- For now, allow all operations for default_user
CREATE POLICY "Allow all operations for default user" ON public.meals
    FOR ALL USING (user_id = 'default_user');

CREATE POLICY "Allow all operations for foods" ON public.foods
    FOR ALL USING (true);

-- Create storage bucket for meal photos
INSERT INTO storage.buckets (id, name, public) 
VALUES ('meal-photos', 'meal-photos', true)
ON CONFLICT (id) DO NOTHING;

-- Storage policy for meal photos
CREATE POLICY "Allow public access to meal photos" ON storage.objects
    FOR ALL USING (bucket_id = 'meal-photos');

-- Add nutrition columns to existing foods table (if they don't exist)
ALTER TABLE public.foods 
ADD COLUMN IF NOT EXISTS protein DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS carbs DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS fat DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS fiber DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS sugar DECIMAL(8,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS sodium DECIMAL(8,2) DEFAULT 0;

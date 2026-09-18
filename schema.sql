-- ==============================================================================
-- NAIJA CHRONICLES — FULL PRODUCTION SUPABASE SCHEMA & POLICIES
-- Run this in your Supabase Project's SQL Editor (https://supabase.com/dashboard)
-- ==============================================================================

-- 1. Create Articles Table
CREATE TABLE IF NOT EXISTS public.articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    dek TEXT,
    category TEXT NOT NULL DEFAULT 'General',
    tag TEXT DEFAULT 'Dispatch',
    author_name TEXT NOT NULL,
    author_role TEXT,
    author_avatar TEXT,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    read_time TEXT DEFAULT '5 min read',
    cover_image TEXT,
    image_caption TEXT,
    featured BOOLEAN DEFAULT false,
    lead_story BOOLEAN DEFAULT false,
    quote TEXT,
    content TEXT NOT NULL,
    views_count INTEGER DEFAULT 0
);

-- 2. Create Subscribers Table (for newsletter signups)
CREATE TABLE IF NOT EXISTS public.subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    email TEXT NOT NULL UNIQUE,
    tier TEXT DEFAULT 'morning-dispatch',
    status TEXT DEFAULT 'active'
);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE public.articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscribers ENABLE ROW LEVEL SECURITY;

-- 4. Set Up Full RLS Policies for Public Anon & Authenticated Users
DROP POLICY IF EXISTS "Allow public read access for articles" ON public.articles;
CREATE POLICY "Allow public read access for articles"
ON public.articles FOR SELECT TO anon, authenticated
USING (true);

DROP POLICY IF EXISTS "Allow article creation" ON public.articles;
CREATE POLICY "Allow article creation"
ON public.articles FOR INSERT TO anon, authenticated
WITH CHECK (true);

DROP POLICY IF EXISTS "Allow article update" ON public.articles;
CREATE POLICY "Allow article update"
ON public.articles FOR UPDATE TO anon, authenticated
USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public newsletter subscriptions" ON public.subscribers;
CREATE POLICY "Allow public newsletter subscriptions"
ON public.subscribers FOR INSERT TO anon, authenticated
WITH CHECK (true);

DROP POLICY IF EXISTS "Allow read subscribers" ON public.subscribers;
CREATE POLICY "Allow read subscribers"
ON public.subscribers FOR SELECT TO authenticated
USING (true);

-- ==============================================================================
-- MIGRATION 20260918000001: Fix RLS Policies for Public Subscriptions & Updates
-- ==============================================================================

-- 1. Ensure anon public role can insert newsletter subscriptions
DROP POLICY IF EXISTS "Allow public newsletter subscriptions" ON public.subscribers;
CREATE POLICY "Allow public newsletter subscriptions"
ON public.subscribers FOR INSERT TO anon, authenticated
WITH CHECK (true);

-- 2. Ensure anon public role can read/insert articles
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

-- ==============================================================================
-- THE CHRONICLE / EDITORIAL MAGAZINE SCHEMA & SEED SCRIPT FOR SUPABASE
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
    tier TEXT DEFAULT 'weekly-dispatch',
    status TEXT DEFAULT 'active'
);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE public.articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscribers ENABLE ROW LEVEL SECURITY;

-- 4. Set Up Policies: Public Read for Articles, Public Insert for Subscribers & CMS Demo
-- Public can read all published articles
CREATE POLICY "Allow public read access for articles"
ON public.articles FOR SELECT USING (true);

-- Allow public / authenticated users to insert articles (for editorial CMS demo)
CREATE POLICY "Allow article creation"
ON public.articles FOR INSERT WITH CHECK (true);

-- Allow public newsletter signups
CREATE POLICY "Allow public newsletter subscriptions"
ON public.subscribers FOR INSERT WITH CHECK (true);

-- 5. Seed Initial Editorial Articles
INSERT INTO public.articles (
    title, slug, dek, category, tag, author_name, author_role, author_avatar,
    read_time, cover_image, image_caption, featured, lead_story, quote, content
) VALUES
(
    'The Architecture of Silence: Why Modern Cities Are Designing Soundless Sanctuaries',
    'architecture-of-silence-modern-cities',
    'In an era of relentless sensory saturation, architects and urban theorists are engineering acoustic refuges — transforming metropolitan density into contemplative stillness.',
    'Architecture & Design',
    'Cover Story',
    'Elena Rostova',
    'Senior Architecture Critic',
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80',
    '7 min read',
    'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600&q=85',
    'The Brutalist Cloister in Kyoto, designed by Studio Kanso (2025). Photo: Kenji Tanaka / The Chronicle.',
    true,
    true,
    'Silence is not the absence of sound; it is the presence of intentional space.',
    '<p class="lead-paragraph">Step into the heart of Tokyo’s Ginza district at noon, and the decibel meter vibrates against 82 dB — the auditory equivalent of a diesel truck idling at your shoulder. Yet descend eighteen steps into the subterranean rotunda of the newly opened Kanso Pavilion, and the ambient noise plummets to 18 dB. It is not deafening; it is profound.</p><p>For the past century, metropolitan architecture prioritized sight and movement: soaring glass facades that reflect the sky, sprawling transit hubs that maximize passenger throughput, and illuminated billboards that command visual attention. But as urban density surges, a quiet revolution is taking root across global design capitals.</p><h3>The Acoustic Geometry of Modern Monasteries</h3><p>Leading acousticians and spatial designers are no longer treating acoustic insulation as an afterthought concealed behind drywall. Instead, sound dissipation is dictating form itself. From the porous travertine colonnades in Milan to the faceted micro-perforated timber domes of Copenhagen, modern structures are sculpted to swallow vibration.</p><blockquote><p>“We spent seventy years engineering buildings to bounce light. We are now learning to absorb friction,” explains Dr. Marcus Vance, chair of Spatial Acoustics at the Zurich Institute of Design.</p></blockquote>'
),
(
    'The Post-Silicon Frontier: How Optical Compute Is Rewriting the Laws of Intelligence',
    'post-silicon-frontier-optical-compute',
    'Photonic processors using light rather than electricity are achieving thousand-fold energy efficiencies, promising a sustainable future for planetary-scale machine cognition.',
    'Technology & Science',
    'Deep Dive',
    'Dr. Aris Thorne',
    'Technology Fellow',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80',
    '9 min read',
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=85',
    'Nanophotonic laser waveguides etched onto synthetic diamond substrate.',
    true,
    false,
    'When computations occur at the speed of photons, latency becomes a theoretical artifact rather than a physical constraint.',
    '<p class="lead-paragraph">For over five decades, Moore''s Law served as the predictable metronome of technological progress. Every eighteen months, transistors shrank, clock speeds climbed, and humanity built increasingly sophisticated abstractions upon silicon foundations. Today, however, the relentless thermodynamics of copper wires have caught up with us.</p><p>Modern AI hyperscale data centers are consuming power at the scale of medium-sized sovereign nations. The bottleneck is no longer mathematical algorithm design; it is thermal dissipation.</p>'
),
(
    'The Rediscovery of Slow Craft in Haute Couture and Industrial Design',
    'rediscovery-of-slow-craft-haute-couture',
    'Against the relentless tides of algorithmic generation and rapid prototyping, master ateliers are championing heirloom permanence and tactile provenance.',
    'Culture & Style',
    'Visual Essay',
    'Camille Laurent',
    'Fashion & Arts Editor',
    'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80',
    '6 min read',
    'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?auto=format&fit=crop&w=1200&q=85',
    'Hand-loomed organic raw silk dyed with fermented indigo in Kyoto. Photo: M. Dubois.',
    true,
    false,
    'In a world of infinite instantaneous copies, the only true luxury is the unrepeatable human hand.',
    '<p class="lead-paragraph">In an airy studio overlooking the Seine in the 11th arrondissement, artisan weavers manipulate a 120-year-old Jacquard loom with the rhythmic precision of concert pianists. There are no computer screens, no automated tensioners, and no hurry.</p><p>It takes four hundred hours to produce six meters of this double-faced wool damask. Every single centimeter bears subtle, indelible variations that machine calibration would categorize as defects — yet these exact irregularities are what elevate the textile to a work of high art.</p>'
)
ON CONFLICT (slug) DO NOTHING;
